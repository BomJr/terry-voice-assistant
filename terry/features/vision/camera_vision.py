"""
Camera Vision - Terry v6.1
HYBRID integration with face-recognition project
Uses local modules for speed, API for management
"""
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import tempfile
from datetime import datetime
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class CameraVisionManager:
    """Manages camera vision with face recognition."""

    def __init__(self, face_recog_path: Optional[str] = None,
                 api_url: Optional[str] = None,
                 use_local: bool = True):
        """
        Initialize Camera Vision Manager.

        Args:
            face_recog_path: Path to face-recognition project
            api_url: URL for face-recognition API
            use_local: Use local modules (faster) vs API only
        """
        self.face_recog_path = face_recog_path or os.getenv("FACE_RECOG_PATH", str(Path.home() / "face-recognition"))
        self.api_url = api_url or "http://localhost:2100"
        self.use_local = use_local

        self.detector = None
        self.recognizer = None
        self.camera = None

        self._local_available = False
        self._api_available = False

        self._init_local_modules()

        logger.info("Camera Vision Manager initialized")

    def _init_local_modules(self):
        """Initialize local face-recognition modules for speed."""
        if not self.use_local:
            logger.info("Local modules disabled, using API only")
            return

        try:
            # Add face-recognition to path
            if Path(self.face_recog_path).exists():
                sys.path.insert(0, self.face_recog_path)

                # Try to import local modules
                from src.face_recognition.detector import create_detector
                from src.face_recognition.recognizer import FaceRecognizer
                from src.camera.stream import CameraStream

                # Initialize components
                self.detector = create_detector({'backend': 'mediapipe'})
                self.recognizer = FaceRecognizer()
                self.camera = CameraStream()

                self._local_available = True
                logger.info("✅ Local face-recognition modules loaded")

            else:
                logger.warning(f"Face-recognition path not found: {self.face_recog_path}")

        except ImportError as e:
            logger.warning(f"Could not load local modules: {e}")
            logger.info("Will use API or screenshot fallback")
        except Exception as e:
            logger.error(f"Error initializing local modules: {e}")

    async def capture_screenshot(self) -> Optional[str]:
        """
        Capture screenshot of current screen.

        Returns:
            Path to screenshot file or None
        """
        try:
            # Create temp file
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"{temp_dir}/terry_screenshot_{timestamp}.png"

            # Use macOS screencapture command
            result = subprocess.run(
                ['screencapture', '-x', screenshot_path],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0 and Path(screenshot_path).exists():
                logger.info(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                logger.error("Screenshot failed")
                return None

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    async def recognize_person(self) -> Optional[Dict[str, Any]]:
        """
        Recognize person using camera (if available).

        Returns:
            Dict with person info or None
        """
        if not self._local_available:
            return {
                'success': False,
                'message': 'Camera recognition not available (local modules not loaded)'
            }

        try:
            # Capture frame from camera
            frame = self.camera.capture_frame()

            if frame is None:
                return {
                    'success': False,
                    'message': 'Could not capture camera frame'
                }

            # Detect faces
            faces = self.detector.detect_faces(frame)

            if not faces:
                return {
                    'success': False,
                    'message': 'No faces detected'
                }

            # Recognize first face
            person = self.recognizer.recognize_face(faces[0])

            return {
                'success': True,
                'person': person.get('name', 'Unknown'),
                'confidence': person.get('confidence', 0.0),
                'face_count': len(faces)
            }

        except Exception as e:
            logger.error(f"Error recognizing person: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    async def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze screenshot (placeholder for GPT-4V integration).

        Args:
            screenshot_path: Path to screenshot

        Returns:
            Analysis results
        """
        # TODO: Integrate with GPT-4V or similar vision model
        # For now, return basic info

        if not Path(screenshot_path).exists():
            return {
                'success': False,
                'message': 'Screenshot file not found'
            }

        file_size = Path(screenshot_path).stat().st_size / 1024  # KB

        return {
            'success': True,
            'message': 'Screenshot captured successfully',
            'path': screenshot_path,
            'size_kb': round(file_size, 2),
            'note': 'Vision analysis requires GPT-4V integration (not implemented yet)'
        }

    async def describe_screen(self) -> str:
        """
        Describe what's on screen (high-level function).

        Returns:
            Description text
        """
        # Capture screenshot
        screenshot_path = await self.capture_screenshot()

        if not screenshot_path:
            return "No pude capturar la pantalla"

        # Analyze (for now, just confirm capture)
        result = await self.analyze_screenshot(screenshot_path)

        if result['success']:
            return f"Capturé la pantalla. Para análisis visual completo, necesito integración con GPT-4V."
        else:
            return "Hubo un error capturando la pantalla"

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from face-recognition API.

        Returns:
            Stats dictionary
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/api/stats",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        'success': False,
                        'message': f'API returned {response.status_code}'
                    }

        except Exception as e:
            logger.error(f"Error getting stats from API: {e}")
            return {
                'success': False,
                'message': f'Could not connect to API: {str(e)}'
            }


# Singleton instance
_camera_vision: Optional[CameraVisionManager] = None


def get_camera_vision() -> CameraVisionManager:
    """
    Get the singleton CameraVisionManager instance.

    Returns:
        CameraVisionManager instance
    """
    global _camera_vision

    if _camera_vision is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("camera_vision", {})

            face_recog_path = config.get("face_recognition_path")
            api_url = config.get("api_url")
            use_local = config.get("use_local_modules", True)

            _camera_vision = CameraVisionManager(
                face_recog_path=face_recog_path,
                api_url=api_url,
                use_local=use_local
            )

        except Exception as e:
            logger.warning(f"Could not load settings for camera vision: {e}")
            _camera_vision = CameraVisionManager()

    return _camera_vision
