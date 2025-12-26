"""
Camera Vision Manager - Terry v6.1
Servicio de cámara siempre activo con:
- Reconocimiento facial
- Detección de presencia
- Análisis de emociones
- Integración con sistema face-recognition
"""
import asyncio
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import cv2
import numpy as np

# Add face-recognition to path
# Get path from settings or use default
from pathlib import Path
FACE_RECOG_PATH = str(Path.home() / "face-recognition")
sys.path.insert(0, FACE_RECOG_PATH)

try:
    from src.camera.stream import CameraStream
    from src.face_recognition.detector import create_detector
    from src.face_recognition.recognizer import FaceRecognizer
    from src.database.manager import DatabaseManager
    from src.utils.config import Config
    FACE_RECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Face recognition not available: {e}")
    FACE_RECOGNITION_AVAILABLE = False

from terry.core.utils.logger import get_logger
from terry.core.config.settings import get_settings

logger = get_logger(__name__)


@dataclass
class Person:
    """Representa una persona detectada."""
    name: str
    confidence: float
    last_seen: datetime
    bbox: tuple  # (x, y, w, h)
    embedding: Optional[np.ndarray] = None
    emotion: Optional[str] = None
    emotion_confidence: float = 0.0


@dataclass
class PresenceState:
    """Estado de presencia actual."""
    people_present: Dict[str, Person] = field(default_factory=dict)
    unknown_count: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    total_detections: int = 0


class CameraVisionManager:
    """
    Gestor de visión por cámara siempre activo.

    Funcionalidades:
    - Reconocimiento facial en tiempo real
    - Detección de presencia
    - Análisis de emociones
    - Notificaciones de cambios
    - API para comandos de voz
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar el gestor de visión.

        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.logger = logger
        self.settings = get_settings()

        # Leer configuración de Terry
        self.camera_config = self.settings.get("camera_vision", {})

        # Cargar configuración de face-recognition
        if config_path is None:
            # Usar ruta de configuración de Terry si está definida
            face_recog_path = self.camera_config.get("face_recognition_path", FACE_RECOG_PATH)
            face_recog_config = self.camera_config.get("face_recognition_config", "config/config.yaml")
            config_path = f"{face_recog_path}/{face_recog_config}"

        self.config = Config.from_yaml(config_path)

        # SOBRESCRIBIR configuración de cámara con la de Terry si está presente
        if self.camera_config.get("camera_url"):
            self._override_camera_config()

        # Componentes de face-recognition
        self.camera: Optional[CameraStream] = None
        self.detector = None
        self.recognizer: Optional[FaceRecognizer] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.known_embeddings: List[Dict] = []

        # URL de cámara (sobrescrita desde Terry settings si existe)
        self.camera_url: Optional[str] = None

        # Estado de presencia
        self.presence = PresenceState()
        self.presence_history = deque(maxlen=100)  # Últimas 100 detecciones

        # Control del servicio
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop_task: Optional[asyncio.Task] = None

        # Callbacks para eventos
        self._on_person_detected: List[Callable] = []
        self._on_person_left: List[Callable] = []
        self._on_presence_changed: List[Callable] = []

        # Configuración (leer de Terry settings)
        self.detection_interval = self.camera_config.get("detection_interval", 1.0)
        self.presence_timeout = self.camera_config.get("presence_timeout", 10.0)
        self.confidence_threshold = self.camera_config.get("confidence_threshold", 0.6)

        # Estadísticas
        self.stats = {
            'total_detections': 0,
            'recognized_count': 0,
            'unknown_count': 0,
            'start_time': None
        }

        self.logger.info("CameraVisionManager initialized")

    def _override_camera_config(self):
        """Sobrescribir configuración de cámara con valores de Terry settings."""
        # Construir URL de cámara desde configuración de Terry
        use_webcam = self.camera_config.get("use_webcam", False)

        if use_webcam:
            # Usar webcam local
            webcam_index = self.camera_config.get("webcam_index", 0)
            self.camera_url = webcam_index  # OpenCV acepta índice para webcams
            self.logger.info(f"Using webcam #{webcam_index}")
        else:
            # Usar cámara IP
            camera_url = self.camera_config.get("camera_url", "")
            username = self.camera_config.get("camera_username", "")
            password = self.camera_config.get("camera_password", "")

            # Si hay credenciales, construir URL con autenticación
            if username and password and "://" in camera_url:
                # Insertar credenciales en la URL
                protocol, rest = camera_url.split("://", 1)
                camera_url = f"{protocol}://{username}:{password}@{rest}"

            self.camera_url = camera_url
            self.logger.info(f"Using IP camera: {camera_url.replace(password, '****') if password else camera_url}")

        self.logger.info("Camera configuration overridden from Terry settings")

    def initialize_components(self) -> bool:
        """
        Inicializar componentes de face-recognition.

        Returns:
            True si se inicializó correctamente
        """
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.error("Face recognition modules not available")
            return False

        try:
            # Inicializar base de datos
            self.db_manager = DatabaseManager(self.config.database)

            # Inicializar detector
            self.detector = create_detector(self.config.detection)

            # Inicializar reconocedor
            self.recognizer = FaceRecognizer(self.config.recognition)

            # Inicializar cámara
            # Si tenemos URL de Terry settings, usar esa; si no, usar config de face-recognition
            if self.camera_url is not None:
                # Crear CameraStream con nuestra URL personalizada
                import cv2
                self.camera = cv2.VideoCapture(self.camera_url)
                if not self.camera.isOpened():
                    raise Exception(f"Could not open camera: {self.camera_url}")
                self.logger.info(f"Camera opened with URL: {self.camera_url}")
            else:
                # Usar configuración de face-recognition
                self.camera = CameraStream(self.config.camera)

            # Cargar embeddings conocidos
            self.reload_known_faces()

            self.logger.info("Face recognition components initialized")
            self.logger.info(f"Loaded {len(self.known_embeddings)} known faces")

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False

    def reload_known_faces(self):
        """Recargar caras conocidas desde la base de datos."""
        if self.db_manager:
            self.known_embeddings = self.db_manager.get_all_embeddings(
                model=self.config.recognition.model
            )
            self.logger.info(f"Reloaded {len(self.known_embeddings)} known faces")

    def start(self) -> bool:
        """
        Iniciar el servicio de cámara en segundo plano.

        Returns:
            True si se inició correctamente
        """
        if self._running:
            self.logger.warning("Camera service already running")
            return True

        # Inicializar componentes
        if not self.initialize_components():
            return False

        # Conectar cámara
        if not self.camera.connect():
            self.logger.error("Failed to connect to camera")
            return False

        self._running = True
        self.stats['start_time'] = datetime.now()

        # Iniciar thread de procesamiento
        self._thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._thread.start()

        self.logger.info("✅ Camera vision service started")
        return True

    def stop(self):
        """Detener el servicio de cámara."""
        if not self._running:
            return

        self._running = False

        # Desconectar cámara
        if self.camera:
            import cv2
            if isinstance(self.camera, cv2.VideoCapture):
                # cv2.VideoCapture
                self.camera.release()
            else:
                # CameraStream de face-recognition
                self.camera.disconnect()

        # Esperar a que termine el thread
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

        self.logger.info("Camera vision service stopped")

    def _processing_loop(self):
        """Loop principal de procesamiento (corre en thread separado)."""
        self.logger.info("Processing loop started")

        while self._running:
            try:
                start_time = time.time()

                # Capturar frame usando el método unificado
                frame = self.capture_frame()

                if frame is not None:
                    # Procesar frame
                    self._process_frame(frame)
                else:
                    # Intentar reconectar
                    self.logger.warning("Frame capture failed, attempting reconnect")
                    if not self.camera.reconnect():
                        self.logger.error("Camera reconnection failed")
                        time.sleep(5.0)  # Esperar antes de reintentar
                        continue

                # Limpiar presencias antiguas
                self._cleanup_old_presences()

                # Esperar hasta el próximo intervalo
                elapsed = time.time() - start_time
                sleep_time = max(0, self.detection_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)

        self.logger.info("Processing loop ended")

    def _process_frame(self, frame: np.ndarray):
        """
        Procesar un frame para detectar y reconocer caras.

        Args:
            frame: Frame capturado de la cámara
        """
        try:
            # Detectar caras
            detections = self.detector.detect(frame)

            self.stats['total_detections'] += len(detections)

            # Procesar cada detección
            current_people = {}

            for detection in detections:
                bbox = detection['bbox']
                x, y, w, h = bbox

                # Extraer cara
                face_img = frame[y:y+h, x:x+w]

                # Generar embedding
                embedding = self.recognizer.generate_embedding(face_img)

                if embedding is None:
                    continue

                # Buscar coincidencia con caras conocidas
                person = self._find_best_match(embedding, bbox)

                if person:
                    current_people[person.name] = person

                    # Evento: persona detectada
                    if person.name not in self.presence.people_present:
                        self._trigger_person_detected(person)
                        self.stats['recognized_count'] += 1

            # Actualizar estado de presencia
            self._update_presence(current_people)

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")

    def _find_best_match(self, embedding: np.ndarray, bbox: tuple) -> Optional[Person]:
        """
        Buscar la mejor coincidencia para un embedding.

        Args:
            embedding: Embedding de la cara detectada
            bbox: Bounding box de la detección

        Returns:
            Person si se encontró coincidencia, None si es desconocido
        """
        if len(self.known_embeddings) == 0:
            return Person(
                name="Unknown",
                confidence=0.0,
                last_seen=datetime.now(),
                bbox=bbox,
                embedding=embedding
            )

        best_match = self.recognizer.find_best_match(
            query_embedding=embedding,
            known_embeddings=self.known_embeddings,
            threshold=self.confidence_threshold
        )

        if best_match:
            person_id = best_match['person_id']
            confidence = best_match['confidence']

            # Obtener nombre de la persona
            person_info = self.db_manager.get_person(person_id)
            name = person_info.get('name', f"Person_{person_id}")

            return Person(
                name=name,
                confidence=confidence,
                last_seen=datetime.now(),
                bbox=bbox,
                embedding=embedding
            )
        else:
            self.stats['unknown_count'] += 1
            return Person(
                name="Unknown",
                confidence=0.0,
                last_seen=datetime.now(),
                bbox=bbox,
                embedding=embedding
            )

    def _update_presence(self, current_people: Dict[str, Person]):
        """
        Actualizar estado de presencia.

        Args:
            current_people: Diccionario de personas detectadas actualmente
        """
        previous_people = set(self.presence.people_present.keys())
        current_people_names = set(current_people.keys())

        # Personas que se fueron
        left_people = previous_people - current_people_names
        for name in left_people:
            person = self.presence.people_present[name]
            self._trigger_person_left(person)

        # Actualizar presencia
        self.presence.people_present = current_people
        self.presence.last_update = datetime.now()

        # Registrar en historial
        self.presence_history.append({
            'timestamp': datetime.now(),
            'people': list(current_people.keys()),
            'count': len(current_people)
        })

        # Evento: cambio de presencia
        if previous_people != current_people_names:
            self._trigger_presence_changed()

    def _cleanup_old_presences(self):
        """Limpiar presencias antiguas que ya no están."""
        now = datetime.now()
        timeout = timedelta(seconds=self.presence_timeout)

        to_remove = []
        for name, person in self.presence.people_present.items():
            if now - person.last_seen > timeout:
                to_remove.append(name)

        for name in to_remove:
            person = self.presence.people_present.pop(name)
            self._trigger_person_left(person)

    # ═══════════════════════════════════════════════════════════
    # EVENTOS / CALLBACKS
    # ═══════════════════════════════════════════════════════════

    def on_person_detected(self, callback: Callable[[Person], None]):
        """Registrar callback para cuando se detecta una persona."""
        self._on_person_detected.append(callback)

    def on_person_left(self, callback: Callable[[Person], None]):
        """Registrar callback para cuando una persona se va."""
        self._on_person_left.append(callback)

    def on_presence_changed(self, callback: Callable[[List[str]], None]):
        """Registrar callback para cambios de presencia."""
        self._on_presence_changed.append(callback)

    def _trigger_person_detected(self, person: Person):
        """Disparar evento de persona detectada."""
        self.logger.info(f"👤 Person detected: {person.name} ({person.confidence:.0%})")
        for callback in self._on_person_detected:
            try:
                callback(person)
            except Exception as e:
                self.logger.error(f"Error in person_detected callback: {e}")

    def _trigger_person_left(self, person: Person):
        """Disparar evento de persona que se fue."""
        self.logger.info(f"👋 Person left: {person.name}")
        for callback in self._on_person_left:
            try:
                callback(person)
            except Exception as e:
                self.logger.error(f"Error in person_left callback: {e}")

    def _trigger_presence_changed(self):
        """Disparar evento de cambio de presencia."""
        people = list(self.presence.people_present.keys())
        self.logger.info(f"🔄 Presence changed: {', '.join(people) if people else 'Nobody'}")
        for callback in self._on_presence_changed:
            try:
                callback(people)
            except Exception as e:
                self.logger.error(f"Error in presence_changed callback: {e}")

    # ═══════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════

    def get_current_presence(self) -> Dict[str, Any]:
        """
        Obtener estado actual de presencia.

        Returns:
            Diccionario con información de presencia
        """
        return {
            'people': [
                {
                    'name': person.name,
                    'confidence': person.confidence,
                    'last_seen': person.last_seen.isoformat(),
                    'bbox': person.bbox
                }
                for person in self.presence.people_present.values()
            ],
            'count': len(self.presence.people_present),
            'last_update': self.presence.last_update.isoformat()
        }

    def who_is_present(self) -> List[str]:
        """
        Obtener lista de nombres de personas presentes.

        Returns:
            Lista de nombres
        """
        return list(self.presence.people_present.keys())

    def is_person_present(self, name: str) -> bool:
        """
        Verificar si una persona específica está presente.

        Args:
            name: Nombre de la persona

        Returns:
            True si está presente
        """
        return name in self.presence.people_present

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio.

        Returns:
            Diccionario con estadísticas
        """
        uptime = None
        if self.stats['start_time']:
            uptime = (datetime.now() - self.stats['start_time']).total_seconds()

        return {
            'running': self._running,
            'uptime_seconds': uptime,
            'total_detections': self.stats['total_detections'],
            'recognized_count': self.stats['recognized_count'],
            'unknown_count': self.stats['unknown_count'],
            'known_faces': len(self.known_embeddings),
            'current_presence_count': len(self.presence.people_present)
        }

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capturar un frame actual de la cámara.

        Returns:
            Frame capturado o None si falla
        """
        if not self.camera:
            return None

        # Detectar tipo de cámara y leer frame apropiadamente
        import cv2
        if isinstance(self.camera, cv2.VideoCapture):
            # Cámara cv2.VideoCapture directa (desde Terry settings)
            if not self.camera.isOpened():
                return None
            success, frame = self.camera.read()
            return frame if success else None
        else:
            # CameraStream de face-recognition
            if not self.camera.is_connected:
                return None
            success, frame = self.camera.read_frame()
            return frame if success else None


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_camera_vision_manager: Optional[CameraVisionManager] = None


def get_camera_vision_manager() -> CameraVisionManager:
    """Obtener la instancia singleton del gestor de cámara."""
    global _camera_vision_manager
    if _camera_vision_manager is None:
        _camera_vision_manager = CameraVisionManager()
    return _camera_vision_manager


def start_camera_service() -> bool:
    """
    Iniciar el servicio de cámara.

    Returns:
        True si se inició correctamente
    """
    manager = get_camera_vision_manager()
    return manager.start()


def stop_camera_service():
    """Detener el servicio de cámara."""
    manager = get_camera_vision_manager()
    manager.stop()
