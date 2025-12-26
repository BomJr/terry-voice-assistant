"""
Home-Alexa - Voice Pipeline
Pipeline completo: Wake Word → STT → Procesamiento → TTS
"""

import asyncio
from typing import Optional
from datetime import datetime
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from llm.command_processor import CommandProcessor
from llm.ollama_client import OllamaClient
from actions.action_executor import ActionExecutor
from utils.session_state import get_session
from utils.audit_logger import get_audit_logger
from utils.logger import get_logger
from ui.terminal_led import TerminalLED, LEDState
from voice.conversation_manager import ConversationManager, ConversationState
import time

logger = get_logger(__name__)


class VoicePipeline:
    """Pipeline completo de voz para Home-Alexa."""

    def __init__(
        self,
        wake_word_enabled: bool = False,
        tts_enabled: bool = True,
        language: str = "es",
        simplify_responses: bool = True,  # v6.0 - Estilo Alexa
        confirm_commands: bool = False,    # v6.0.1 UX - Confirmar comandos audiblemente
        wake_timeout: int = 10             # v6.0.1 UX - Timeout para wake word (segundos)
    ):
        """
        Inicializa el pipeline de voz.

        Args:
            wake_word_enabled: Si activar wake word detection
            tts_enabled: Si activar respuestas de voz
            language: Idioma (es o en)
            simplify_responses: Si simplificar respuestas TTS estilo Alexa
            confirm_commands: Si confirmar comandos escuchados antes de ejecutar
            wake_timeout: Segundos de espera para wake word (10=normal, 15=más tiempo, 5=rápido)
        """
        self.wake_word_enabled = wake_word_enabled
        self.tts_enabled = tts_enabled
        self.language = language
        self.simplify_responses = simplify_responses
        self.confirm_commands = confirm_commands
        self.wake_timeout = wake_timeout

        # Cargar configuración de micrófono si existe (v6.0)
        microphone_index = None
        try:
            with open(".terry_microphone", "r") as f:
                microphone_index = int(f.read().strip())
                logger.info(f"Usando micrófono configurado: #{microphone_index}")
        except:
            pass

        # Componentes ULTRA-RÁPIDOS (modo Alexa)
        self.stt = SpeechToText(
            language=language,
            model_size="tiny",  # Solo fallback (Whisper)
            use_whisper=False,  # Google primero (0.5s vs 2s)
            energy_threshold=150,  # Más sensible (v6.0 - antes 300)
            dynamic_energy=True,
            pause_threshold=0.8,  # v6.0.1 - Pausas más largas para "terry pon música"
            microphone_index=microphone_index  # v6.0
        )
        self.tts = TextToSpeech(
            rate=200,  # Un poco más rápido
            volume=0.95,
            optimize_for_voice=True,
            simplify_responses=simplify_responses  # v6.0 - Configurable
        ) if tts_enabled else None

        # Wake words para Terry (v6.0.1 - variaciones de "terry" para mejor detección)
        self.wake_words = [
            "terry", "teri", "terri", "terrie",  # Variaciones de Terry
            "hey mac", "oye mac", "ok mac"       # Alternativas en español
        ]
        self.assistant_name = "Terry"

        # LLM y executor
        self.llm_client = OllamaClient()
        self.command_processor = CommandProcessor(self.llm_client, language)
        self.action_executor = ActionExecutor()

        # Estado
        self.session = get_session()
        self.audit = get_audit_logger()

        # LED feedback visual (pulse desactivado para evitar spam en terminal)
        self.led = TerminalLED(enabled=True, pulse_enabled=False)

        # Conversation manager para multi-turno sin wake word
        self.conversation = ConversationManager(window_seconds=8.0, auto_expire=True)

        # v6.1 - Persistent Memory (initialized asynchronously)
        self.memory = None
        self._memory_enabled = False

        # v6.1 - Pattern Learning (initialized asynchronously)
        self.pattern_learner = None
        self._pattern_learning_enabled = False

        # v6.1 - Context Tracking (initialized asynchronously)
        self.context_manager = None
        self._context_tracking_enabled = False

        # v6.1 - Intelligent Suggestions (initialized asynchronously)
        self.suggestions = None
        self._suggestions_enabled = False

        # v6.1 - Camera Vision (initialized asynchronously)
        self.camera_vision = None
        self._camera_vision_enabled = False

        # v6.1 - Scheduler (initialized asynchronously)
        self.scheduler = None
        self._scheduler_enabled = False

        # v6.1 - Conditional Triggers (initialized asynchronously)
        self.triggers_engine = None
        self._triggers_enabled = False

        # v6.1 - Macro Recorder (initialized asynchronously)
        self.macro_recorder = None
        self._macros_enabled = False

        # v6.1 - Barge-in (initialized asynchronously)
        self.barge_in = None
        self._barge_in_enabled = False

        # v6.1 - Frustration Detection (initialized asynchronously)
        self.frustration_detector = None
        self._frustration_enabled = False

        # v6.1 - Plugin System (initialized asynchronously)
        self.plugin_system = None
        self._plugins_enabled = False

        # v6.1 - REST API (initialized asynchronously)
        self.api = None
        self._api_enabled = False

        self.is_running = False

    async def initialize_memory(self):
        """
        Inicializa el sistema de memoria persistente (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from memory.memory_manager import MemoryManager

            # Check if memory is enabled in settings
            memory_config = settings.get("persistent_memory", {})
            self._memory_enabled = memory_config.get("enabled", False)

            if self._memory_enabled:
                # Get database path from settings or use default
                db_path = memory_config.get("database_path", "data/memory.db")

                # Initialize memory manager
                self.memory = MemoryManager(db_path=db_path)
                await self.memory.initialize()

                logger.info("✅ Persistent Memory initialized")
            else:
                logger.info("Persistent Memory disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize memory: {e}")
            self._memory_enabled = False
            self.memory = None

    async def initialize_pattern_learning(self):
        """
        Inicializa el sistema de aprendizaje de patrones (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from memory.pattern_learner import get_pattern_learner

            # Check if pattern learning is enabled
            pl_config = settings.get("pattern_learning", {})
            self._pattern_learning_enabled = pl_config.get("enabled", False)

            if self._pattern_learning_enabled:
                self.pattern_learner = get_pattern_learner()
                logger.info("✅ Pattern Learning initialized")
            else:
                logger.info("Pattern Learning disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize pattern learning: {e}")
            self._pattern_learning_enabled = False
            self.pattern_learner = None

    async def initialize_context_tracking(self):
        """
        Inicializa el sistema de seguimiento de contexto (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from memory.context_manager import get_context_manager

            # Check if context tracking is enabled
            ct_config = settings.get("context_tracking", {})
            self._context_tracking_enabled = ct_config.get("enabled", False)

            if self._context_tracking_enabled:
                self.context_manager = get_context_manager()
                logger.info("✅ Context Tracking initialized")
            else:
                logger.info("Context Tracking disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize context tracking: {e}")
            self._context_tracking_enabled = False
            self.context_manager = None

    async def initialize_suggestions(self):
        """
        Inicializa el sistema de sugerencias inteligentes (v6.1).
        Debe llamarse después de inicializar pattern learning y context tracking.
        """
        try:
            from config.settings import settings
            from memory.intelligent_suggestions import get_intelligent_suggestions

            # Check if suggestions are enabled
            sugg_config = settings.get("intelligent_suggestions", {})
            self._suggestions_enabled = sugg_config.get("enabled", False)

            if self._suggestions_enabled:
                self.suggestions = get_intelligent_suggestions()

                # Initialize with pattern learner and context manager
                self.suggestions.initialize(
                    pattern_learner=self.pattern_learner,
                    context_manager=self.context_manager
                )

                logger.info("✅ Intelligent Suggestions initialized")
            else:
                logger.info("Intelligent Suggestions disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize suggestions: {e}")
            self._suggestions_enabled = False
            self.suggestions = None

    async def initialize_camera_vision(self):
        """
        Inicializa el sistema de visión por cámara (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from vision.camera_vision import get_camera_vision

            # Check if camera vision is enabled in settings
            camera_config = settings.get("camera_vision", {})
            self._camera_vision_enabled = camera_config.get("enabled", False)

            if self._camera_vision_enabled:
                # Get camera vision manager
                self.camera_vision = get_camera_vision()
                logger.info("✅ Camera Vision initialized")
            else:
                logger.info("Camera Vision disabled in settings (opt-in feature)")

        except Exception as e:
            logger.warning(f"Could not initialize camera vision: {e}")
            self._camera_vision_enabled = False
            self.camera_vision = None

    async def initialize_scheduler(self):
        """
        Inicializa el sistema de rutinas programadas (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from scheduler.cron_manager import get_cron_manager

            # Check if scheduler is enabled in settings
            scheduler_config = settings.get("scheduler", {})
            self._scheduler_enabled = scheduler_config.get("enabled", False)

            if self._scheduler_enabled:
                # Get scheduler manager
                self.scheduler = get_cron_manager()

                # Set command executor (so scheduler can run commands)
                self.scheduler.set_command_executor(self.process_voice_command)

                # Start the scheduler
                await self.scheduler.start()

                logger.info("✅ Scheduler initialized and started")
            else:
                logger.info("Scheduler disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize scheduler: {e}")
            self._scheduler_enabled = False
            self.scheduler = None

    async def initialize_triggers(self):
        """
        Inicializa el sistema de triggers condicionales (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from triggers.conditional_engine import get_conditional_engine

            # Check if triggers are enabled in settings
            triggers_config = settings.get("triggers", {})
            self._triggers_enabled = triggers_config.get("enabled", False)

            if self._triggers_enabled:
                # Get triggers engine
                self.triggers_engine = get_conditional_engine()

                # Set command executor (so triggers can run commands)
                self.triggers_engine.set_command_executor(self.process_voice_command)

                # Start the engine
                await self.triggers_engine.start()

                logger.info("✅ Conditional Triggers initialized and started")
            else:
                logger.info("Conditional Triggers disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize triggers: {e}")
            self._triggers_enabled = False
            self.triggers_engine = None

    async def initialize_macros(self):
        """
        Inicializa el sistema de grabación de macros (v6.1).
        Debe llamarse después de crear el pipeline.
        """
        try:
            from config.settings import settings
            from macros.macro_recorder import get_macro_recorder

            # Check if macros are enabled in settings
            macros_config = settings.get("macros", {})
            self._macros_enabled = macros_config.get("enabled", False)

            if self._macros_enabled:
                # Get macro recorder
                self.macro_recorder = get_macro_recorder()

                # Set command executor (so macros can execute commands)
                self.macro_recorder.set_command_executor(self.process_voice_command)

                logger.info("✅ Macro Recorder initialized")
            else:
                logger.info("Macro Recorder disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize macros: {e}")
            self._macros_enabled = False
            self.macro_recorder = None

    async def initialize_barge_in(self):
        """Initialize barge-in system (v6.1)."""
        try:
            from config.settings import settings
            from interruption.barge_in import get_barge_in

            config = settings.get("barge_in", {})
            self._barge_in_enabled = config.get("enabled", False)

            if self._barge_in_enabled:
                self.barge_in = get_barge_in()
                logger.info("✅ Barge-in initialized")
            else:
                logger.info("Barge-in disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize barge-in: {e}")
            self._barge_in_enabled = False
            self.barge_in = None

    async def initialize_frustration_detection(self):
        """Initialize frustration detection (v6.1)."""
        try:
            from config.settings import settings
            from emotion.frustration_detector import get_frustration_detector

            config = settings.get("frustration_detection", {})
            self._frustration_enabled = config.get("enabled", False)

            if self._frustration_enabled:
                self.frustration_detector = get_frustration_detector()
                logger.info("✅ Frustration Detection initialized")
            else:
                logger.info("Frustration Detection disabled in settings (opt-in)")

        except Exception as e:
            logger.warning(f"Could not initialize frustration detection: {e}")
            self._frustration_enabled = False
            self.frustration_detector = None

    async def initialize_plugins(self):
        """Initialize plugin system (v6.1)."""
        try:
            from config.settings import settings
            from plugins.plugin_system import get_plugin_system

            config = settings.get("plugins", {})
            self._plugins_enabled = config.get("enabled", False)

            if self._plugins_enabled:
                self.plugin_system = get_plugin_system()
                logger.info("✅ Plugin System initialized")
            else:
                logger.info("Plugin System disabled in settings")

        except Exception as e:
            logger.warning(f"Could not initialize plugins: {e}")
            self._plugins_enabled = False
            self.plugin_system = None

    async def initialize_api(self):
        """Initialize REST API (v6.1)."""
        try:
            from config.settings import settings
            from api.rest_api import get_api

            config = settings.get("rest_api", {})
            self._api_enabled = config.get("enabled", False)

            if self._api_enabled:
                self.api = get_api()
                self.api.set_command_executor(self.process_voice_command)
                logger.info("✅ REST API initialized")
                logger.info(f"API available at http://{self.api.host}:{self.api.port}")
            else:
                logger.info("REST API disabled in settings (opt-in)")

        except Exception as e:
            logger.warning(f"Could not initialize API: {e}")
            self._api_enabled = False
            self.api = None

    def _needs_immediate_feedback(self, text: str) -> bool:
        """
        Determina si un comando necesita feedback inmediato mientras procesa (v6.0).

        Args:
            text: Comando del usuario

        Returns:
            True si necesita feedback inmediato
        """
        # Comandos que típicamente son lentos
        slow_keywords = [
            "busca", "search", "qué tiempo", "weather", "clima",
            "dime", "cuéntame", "explica", "qué es", "quién es",
            "cómo", "por qué", "cuándo", "cuánto"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in slow_keywords)

    async def process_voice_command(self, text: str) -> str:
        """
        Procesa un comando de voz.

        Args:
            text: Texto del comando

        Returns:
            Respuesta del asistente
        """
        start_time = time.time()

        try:
            # v6.1 - Resolve pronouns and implicit context
            original_text = text
            if self._context_tracking_enabled and self.context_manager:
                text = self.context_manager.resolve_pronouns(text)
                if text != original_text:
                    logger.info(f"Context resolved: '{original_text}' → '{text}'")

            # Feedback inmediato para comandos lentos (v6.0)
            if self._needs_immediate_feedback(text) and self.tts:
                self.tts.speak("Procesando")

            # Procesar comando
            result = await self.command_processor.process_command(
                user_input=text,
                context=self.session.get_conversation_context(),
                language=self.language
            )

            # Ejecutar acciones
            actions = result.get("actions", [])
            response_text = result.get("response", "")

            if actions:
                execution_result = await self.action_executor.execute_actions(actions)

                # Actualizar respuesta si hay resultados
                if not execution_result.success:
                    response_text = f"{response_text}. Algunas acciones fallaron."

            # Registrar en auditoría
            execution_time = time.time() - start_time
            self.audit.log_command(
                user_input=text,
                intent=result.get("intent", "unknown"),
                actions=actions,
                success=True,
                response=response_text,
                execution_time=execution_time,
                cached=result.get("cached", False)
            )

            # Registrar en sesión
            self.session.record_command(
                user_input=text,
                intent=result.get("intent", "unknown"),
                success=True,
                response=response_text
            )

            # v6.1 - Record command in macro if recording
            if self._macros_enabled and self.macro_recorder:
                try:
                    if self.macro_recorder.is_recording():
                        self.macro_recorder.record_command(text)
                except Exception as e:
                    logger.debug(f"Could not record in macro: {e}")

            # v6.1 - Save to persistent memory
            if self._memory_enabled and self.memory:
                try:
                    await self.memory.save_interaction(
                        transcription=text,
                        intent=result.get("intent"),
                        response=response_text,
                        actions=actions if actions else None,
                        language=self.language,
                        processing_time=execution_time
                    )
                except Exception as e:
                    logger.debug(f"Could not save to memory: {e}")

            # v6.1 - Record pattern for learning
            if self._pattern_learning_enabled and self.pattern_learner:
                try:
                    # Get context (could include active app, etc.)
                    context = {}
                    # TODO: Add active app detection if needed

                    self.pattern_learner.record_command(
                        command=text,
                        timestamp=datetime.now(),
                        context=context
                    )
                except Exception as e:
                    logger.debug(f"Could not record pattern: {e}")

            # v6.1 - Update context tracking
            if self._context_tracking_enabled and self.context_manager:
                try:
                    self.context_manager.update_context(
                        command=text,
                        response=response_text,
                        actions=actions if actions else None
                    )
                except Exception as e:
                    logger.debug(f"Could not update context: {e}")

            # v6.1 - Frustration detection
            if self._frustration_enabled and self.frustration_detector:
                try:
                    self.frustration_detector.record_command(
                        command=text,
                        success=result.get("success", True)
                    )

                    # Check for frustration
                    frustration = self.frustration_detector.detect_frustration()
                    if frustration['frustrated'] and frustration.get('suggestion'):
                        # Optionally add empathetic response
                        logger.info(f"Frustration detected: {frustration['suggestion']}")
                except Exception as e:
                    logger.debug(f"Could not detect frustration: {e}")

            return response_text

        except Exception as e:
            logger.error(f"Error procesando comando de voz: {e}")
            return "Lo siento, hubo un error procesando tu comando"

    async def run_once(self) -> bool:
        """
        Ejecuta un ciclo completo de voz: escuchar → procesar → responder.

        Returns:
            True si se procesó un comando, False si hubo error
        """
        try:
            # 1. Escuchar (STT)
            self.led.set_state(LEDState.LISTENING)
            print("\n" + "=" * 60)
            text = self.stt.listen_once()

            if not text:
                self.led.set_state(LEDState.IDLE)
                return False

            # Mostrar lo que se entendió
            print(f"\n💬 Tú: {text}")

            # 2. Procesar
            self.led.set_state(LEDState.PROCESSING)
            response = await self.process_voice_command(text)

            # Mostrar respuesta
            print(f"🤖 Mac: {response}")

            # 3. Responder con voz (TTS)
            if self.tts_enabled and self.tts and response:
                print(f"🔊 Hablando: '{response[:50]}{'...' if len(response) > 50 else ''}'")
                self.led.set_state(LEDState.RESPONDING)
                self.tts.speak(response)
                # Iniciar ventana de conversación si wake word habilitado
                if self.wake_word_enabled:
                    self.conversation.start_conversation()
                    self.led.set_state(LEDState.CONVERSATION)
                else:
                    self.led.set_state(LEDState.IDLE)
            else:
                print(f"⚠️  TTS OMITIDO - enabled:{self.tts_enabled}, tts:{self.tts is not None}, len(response):{len(response) if response else 0}")

            print("=" * 60)

            return True

        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            self.led.stop()
            return False
        except Exception as e:
            logger.error(f"Error en run_once: {e}")
            self.led.set_state(LEDState.ERROR)
            await asyncio.sleep(1)  # Mostrar error 1s
            self.led.set_state(LEDState.IDLE)
            return False

    async def run_loop(self):
        """Loop continuo de voz con wake word opcional."""
        self.is_running = True

        print("\n" + "=" * 60)
        print(f"🎤 {self.assistant_name.upper()} v6.0 - MODO VOZ ULTRA-RÁPIDO")
        print("=" * 60)

        # Verificar micrófono (v6.0 - diagnóstico)
        try:
            import speech_recognition as sr
            mic = sr.Microphone()
            print(f"✅ Micrófono detectado: {mic.device_index}")
            print(f"   Umbral de energía: {self.stt.recognizer.energy_threshold}")
        except Exception as e:
            print(f"⚠️  Advertencia micrófono: {e}")
            print(f"   Verifica permisos en Preferencias del Sistema > Seguridad > Micrófono")

        if self.wake_word_enabled:
            print(f"💬 Di '{self.wake_words[0]}' para activar")
            print("🔒 Solo escucha cuando dices la palabra de activación")
        else:
            print("💬 Habla cuando quieras (o presiona Ctrl+C para salir)")
            print("⚡ Escucha continuamente - Modo Alexa")

        print("=" * 60)
        self.led.newline()

        # Saludo inicial
        if self.tts_enabled and self.tts:
            self.led.set_state(LEDState.RESPONDING)
            self.tts.speak(f"Hola, soy {self.assistant_name}")
            self.led.set_state(LEDState.IDLE)

        while self.is_running:
            try:
                if self.wake_word_enabled:
                    # Verificar si estamos en ventana de conversación
                    if self.conversation.is_in_conversation():
                        # CONVERSACIÓN ACTIVA - No requiere wake word
                        remaining = self.conversation.get_remaining_time()
                        self.led.set_state(LEDState.CONVERSATION)
                        print(f"\n💬 Escuchando follow-up ({remaining:.0f}s restantes)...")

                        # Escuchar sin wake word
                        text = self.stt.listen_once(timeout=8)

                        if text:
                            # Comando recibido - extender ventana
                            print(f"\n💬 Tú: {text}")
                            self.led.set_state(LEDState.PROCESSING)
                            response = await self.process_voice_command(text)
                            print(f"🤖 {self.assistant_name}: {response}")

                            # v6.0 - Responder con voz
                            if self.tts_enabled and self.tts and response:
                                print(f"🔊 Hablando: '{response[:50]}{'...' if len(response) > 50 else ''}'")
                                self.led.set_state(LEDState.RESPONDING)
                                self.tts.speak(response)
                                # Extender ventana para permitir más follow-ups
                                self.conversation.extend_window()
                                self.led.set_state(LEDState.CONVERSATION)
                            else:
                                print(f"⚠️  TTS OMITIDO - enabled:{self.tts_enabled}, tts:{self.tts is not None}, len(response):{len(response) if response else 0}")
                        else:
                            # Timeout - expirar conversación
                            print("💤 Conversación finalizada (timeout)")
                            self.conversation.expire_conversation()
                            self.led.set_state(LEDState.IDLE)
                    else:
                        # Modo wake word normal: esperar activación (tipo Alexa)
                        self.led.set_state(LEDState.IDLE)
                        print(f"\n💤 Esperando wake word...")
                        print(f"   💡 Di: '{self.wake_words[0]} pon música' (todo de una vez)")
                        print(f"   o: '{self.wake_words[0]}' → espera beep → 'pon música'")

                        detected, comando = self.stt.listen_for_wake_word(
                            self.wake_words,
                            timeout=self.wake_timeout  # v6.0.1 UX - Configurable
                        )

                        if detected:
                            # Wake word detectada - PITIDO (tipo Alexa)
                            self.led.set_state(LEDState.LISTENING)
                            if self.tts:
                                self.tts.play_beep("wake")  # v6.0.1 - Beep diferenciado

                            if comando:
                                # Comando directo: "terry pon música"
                                print(f"\n💬 Tú: {comando}")

                                # v6.0.1 UX - Confirmación audible opcional
                                if self.confirm_commands and self.tts:
                                    # Extraer primera parte del comando para confirmar
                                    comando_corto = comando.split()[0] if comando.split() else comando
                                    self.tts.speak(comando_corto)
                                    self.tts.play_beep("processing")

                                self.led.set_state(LEDState.PROCESSING)
                                response = await self.process_voice_command(comando)
                                print(f"🤖 {self.assistant_name}: {response}")

                                # v6.0 - Responder con voz
                                if self.tts_enabled and self.tts and response:
                                    print(f"🔊 Hablando: '{response[:50]}{'...' if len(response) > 50 else ''}'")
                                    self.led.set_state(LEDState.RESPONDING)
                                    self.tts.speak(response)
                                    # Iniciar ventana de conversación
                                    self.conversation.start_conversation()
                                    self.led.set_state(LEDState.CONVERSATION)
                                else:
                                    print(f"⚠️  TTS OMITIDO - enabled:{self.tts_enabled}, tts:{self.tts is not None}, len(response):{len(response) if response else 0}")
                            else:
                                # Solo wake word, esperar comando
                                print("\n🎤 Escuchando comando...")
                                print("   💡 Ejemplos: 'pon música', 'qué hora es', 'abre safari'")

                                # v6.0.1 UX - Intentar escuchar comando con retry
                                max_retries = 2
                                for retry in range(max_retries):
                                    comando_result = await self.run_once()
                                    if comando_result:
                                        break
                                    elif retry < max_retries - 1:
                                        if self.tts:
                                            self.tts.play_beep("error")
                                            self.tts.speak("No te escuché, repite por favor")
                                        print("   ⚠️  No se escuchó comando, intenta de nuevo...")
                                    else:
                                        if self.tts:
                                            self.tts.play_beep("error")
                                            self.tts.speak("Cancelado")
                                        print("   ❌ Timeout - cancelando")
                        else:
                            # Timeout esperando wake word - mensaje útil
                            print("   ⏱️  Timeout (no se detectó wake word)")
                            continue
                else:
                    # Modo continuo: escuchar siempre
                    self.led.set_state(LEDState.LISTENING)
                    await self.run_once()

                # Pausa mínima entre comandos (ultra-rápido)
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n\n👋 Saliendo...")
                self.led.stop()
                break
            except Exception as e:
                logger.error(f"Error en loop: {e}")
                self.led.set_state(LEDState.ERROR)
                await asyncio.sleep(1)
                self.led.set_state(LEDState.IDLE)

        # Despedida
        if self.tts_enabled and self.tts:
            self.led.set_state(LEDState.RESPONDING)
            self.tts.speak("Hasta luego")
            self.led.stop()

    def stop(self):
        """Detiene el pipeline."""
        self.is_running = False
        if self.tts:
            self.tts.stop()
        if self.led:
            self.led.stop()


async def main():
    """Función principal."""
    import sys

    # Permitir activar wake word con argumento
    wake_word_enabled = "--wake-word" in sys.argv or "-w" in sys.argv

    # v6.0 - Permitir frases completas (no simplificadas)
    simplify_responses = "--full-responses" not in sys.argv

    # v6.0.1 UX - Confirmación audible
    confirm_commands = "--confirm-commands" in sys.argv or "--confirm" in sys.argv

    # v6.0.1 UX - Timeout configurable
    wake_timeout = 10  # default
    for i, arg in enumerate(sys.argv):
        if arg == "--timeout" and i + 1 < len(sys.argv):
            try:
                wake_timeout = int(sys.argv[i + 1])
                wake_timeout = max(3, min(30, wake_timeout))  # Entre 3 y 30 segundos
            except ValueError:
                pass

    # Crear pipeline mejorado v6.0.1 UX
    pipeline = VoicePipeline(
        wake_word_enabled=wake_word_enabled,
        tts_enabled=True,
        language="es",
        simplify_responses=simplify_responses,
        confirm_commands=confirm_commands,
        wake_timeout=wake_timeout
    )

    # v6.1 - Initialize persistent memory
    await pipeline.initialize_memory()

    # v6.1 - Initialize pattern learning
    await pipeline.initialize_pattern_learning()

    # v6.1 - Initialize context tracking
    await pipeline.initialize_context_tracking()

    # v6.1 - Initialize intelligent suggestions (depends on pattern learning and context)
    await pipeline.initialize_suggestions()

    # v6.1 - Initialize camera vision
    await pipeline.initialize_camera_vision()

    # v6.1 - Initialize scheduler
    await pipeline.initialize_scheduler()

    # v6.1 - Initialize conditional triggers
    await pipeline.initialize_triggers()

    # v6.1 - Initialize macro recorder
    await pipeline.initialize_macros()

    # v6.1 - Initialize barge-in
    await pipeline.initialize_barge_in()

    # v6.1 - Initialize frustration detection
    await pipeline.initialize_frustration_detection()

    # v6.1 - Initialize plugin system
    await pipeline.initialize_plugins()

    # v6.1 - Initialize REST API
    await pipeline.initialize_api()

    # Ejecutar
    await pipeline.run_loop()


if __name__ == "__main__":
    asyncio.run(main())
