#!/usr/bin/env python3
"""
Home-Alexa - Asistente de Voz Personal
Main entry point que orquesta todos los módulos
"""

import asyncio
import signal
import sys
from pathlib import Path

from terry.core.config.settings import get_settings
from terry.core.voice.pipeline import VoicePipeline
from terry.core.llm.processor import CommandProcessor
from terry.core.memory.manager import MemoryManager
from terry.core.actions.executor import ActionExecutor
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class HomeAlexa:
    """Orquestador principal del asistente."""

    def __init__(self):
        self.config = Config()
        self.event_bus = EventBus()
        self.state_machine = StateMachine()

        # Componentes principales
        self.audio_manager: AudioManager = None
        self.wakeword_detector: WakeWordDetector = None
        self.stt_engine: MLXWhisperEngine = None
        self.tts_engine: PiperEngine = None
        self.llm_client: OllamaClient = None
        self.command_processor: CommandProcessor = None
        self.memory_manager: MemoryManager = None
        self.context_builder: ContextBuilder = None
        self.action_executor: ActionExecutor = None

        # Control de ejecución
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def initialize(self):
        """Inicializa todos los componentes."""
        logger.info(f"=== Inicializando {self.config.name} v{self.config.version} ===")

        # Audio Manager
        logger.info("Inicializando Audio Manager...")
        self.audio_manager = AudioManager(
            sample_rate=self.config.audio.sample_rate,
            channels=self.config.audio.channels,
            chunk_size=self.config.audio.chunk_size,
            buffer_seconds=self.config.audio.buffer_seconds,
            vad_aggressiveness=self.config.audio.vad_aggressiveness,
            input_device=self.config.audio.input_device,
            output_device=self.config.audio.output_device
        )
        await self.audio_manager.initialize()

        # Wake Word Detector
        logger.info("Inicializando Wake Word Detector...")
        self.wakeword_detector = WakeWordDetector(
            wake_phrase=self.config.wakeword.phrase,
            threshold=self.config.wakeword.threshold,
            sample_rate=self.config.audio.sample_rate
        )
        await self.wakeword_detector.initialize()

        # STT Engine
        logger.info("Inicializando Speech-to-Text...")
        self.stt_engine = MLXWhisperEngine(
            model=self.config.stt.model,
            compute_type=self.config.stt.mlx_whisper.compute_type
        )
        await self.stt_engine.load_model()

        # TTS Engine
        logger.info("Inicializando Text-to-Speech...")
        self.tts_engine = PiperEngine(
            voices=self.config.tts.piper.voices,
            speed=self.config.tts.piper.speed,
            cache_enabled=self.config.tts.piper.cache_enabled
        )
        await self.tts_engine.initialize()

        # LLM Client
        logger.info("Inicializando LLM Client...")
        self.llm_client = OllamaClient(
            host=self.config.llm.ollama.host,
            model=self.config.llm.ollama.model,
            fallback_model=self.config.llm.ollama.fallback_model,
            timeout=self.config.llm.ollama.timeout_seconds,
            temperature=self.config.llm.ollama.temperature,
            max_tokens=self.config.llm.ollama.max_tokens
        )
        await self.llm_client.initialize()

        # Command Processor
        logger.info("Inicializando Command Processor...")
        self.command_processor = CommandProcessor(
            llm_client=self.llm_client,
            default_language=self.config.default_language
        )

        # Memory Manager
        logger.info("Inicializando Memory Manager...")
        self.memory_manager = MemoryManager(
            db_path=self.config.get_absolute_path(self.config.memory.database_path)
        )
        await self.memory_manager.initialize()

        # Context Builder
        logger.info("Inicializando Context Builder...")
        self.context_builder = ContextBuilder(
            memory_manager=self.memory_manager,
            context_window=self.config.memory.context_window
        )

        # Action Executor
        logger.info("Inicializando Action Executor...")
        self.action_executor = ActionExecutor(
            confirmation_level=self.config.actions.confirmation_level,
            execution_timeout=self.config.actions.execution_timeout_seconds,
            tts_engine=self.tts_engine,
            stt_engine=self.stt_engine,
            audio_manager=self.audio_manager
        )

        # Registrar event handlers
        self._register_event_handlers()

        # Iniciar procesador de eventos
        await self.event_bus.start_processor()

        logger.info("=== Sistema inicializado correctamente ===")

    def _register_event_handlers(self):
        """Registra los manejadores de eventos."""
        # State machine transitions en el event bus
        self.state_machine.on_transition(self._on_state_change)

        # Wake word detection
        self.event_bus.subscribe(EventTypes.WAKE_DETECTED, self._handle_wake_detected)

        # STT events
        self.event_bus.subscribe(EventTypes.TRANSCRIPTION_COMPLETE, self._handle_transcription)
        self.event_bus.subscribe(EventTypes.TRANSCRIPTION_ERROR, self._handle_stt_error)

        # LLM events
        self.event_bus.subscribe(EventTypes.LLM_RESPONSE, self._handle_llm_response)
        self.event_bus.subscribe(EventTypes.LLM_ERROR, self._handle_llm_error)

        # Action events
        self.event_bus.subscribe(EventTypes.ACTION_COMPLETE, self._handle_action_complete)
        self.event_bus.subscribe(EventTypes.ACTION_ERROR, self._handle_action_error)
        self.event_bus.subscribe(EventTypes.CONFIRMATION_REQUIRED, self._handle_confirmation_required)

        # TTS events
        self.event_bus.subscribe(EventTypes.TTS_COMPLETE, self._handle_tts_complete)

    async def _on_state_change(self, from_state: State, to_state: State):
        """Handler para cambios de estado."""
        await self.event_bus.emit(Event(
            type=EventTypes.STATE_CHANGED,
            data={"from": from_state.name, "to": to_state.name}
        ))

    async def _handle_wake_detected(self, event: Event):
        """Handler para wake word detectado."""
        logger.info("Wake word detectado!")

        if not self.state_machine.transition(State.WAKE_DETECTED):
            return

        # Reproducir sonido de confirmación si está configurado
        ready_msg = self.config.responses.ready.get(self.config.default_language, "Ready")
        audio_data = await self.tts_engine.synthesize(ready_msg, self.config.default_language)
        await self.audio_manager.play(audio_data)

        # Capturar comando
        self.state_machine.transition(State.LISTENING)

        try:
            audio_data = await self.audio_manager.capture_until_silence(
                max_seconds=self.config.wakeword.post_wake_capture_seconds,
                silence_threshold_seconds=self.config.wakeword.silence_threshold_seconds,
                pre_buffer_seconds=0.5
            )

            if len(audio_data) > 0:
                # Transcribir
                await self.event_bus.emit(Event(type=EventTypes.TRANSCRIPTION_STARTED))
                text, detected_lang = await self.stt_engine.transcribe(audio_data)

                await self.event_bus.emit(Event(
                    type=EventTypes.TRANSCRIPTION_COMPLETE,
                    data={"text": text, "language": detected_lang}
                ))
            else:
                logger.warning("No se capturó audio suficiente")
                self.state_machine.transition(State.IDLE)

        except Exception as e:
            logger.error(f"Error capturando audio: {e}")
            await self.event_bus.emit(Event(
                type=EventTypes.TRANSCRIPTION_ERROR,
                data={"error": str(e)}
            ))

    async def _handle_transcription(self, event: Event):
        """Handler para transcripción completa."""
        text = event.data.get("text", "").strip()

        if not text:
            logger.warning("Transcripción vacía")
            self.state_machine.transition(State.IDLE)
            return

        logger.info(f"Usuario dijo: {text}")

        # Transición a PROCESSING
        if not self.state_machine.transition(State.PROCESSING):
            return

        try:
            # Obtener contexto de memoria
            context = await self.context_builder.build(
                current_input=text,
                language=self.config.default_language
            )

            # Procesar con LLM
            await self.event_bus.emit(Event(type=EventTypes.LLM_PROCESSING))

            response = await self.command_processor.process_command(
                user_input=text,
                context=context,
                language=self.config.default_language
            )

            # Guardar en memoria
            await self.memory_manager.save_interaction(
                transcription=text,
                intent=response.get("intent"),
                response=response.get("response", ""),
                actions=response.get("actions", []),
                language=response.get("language", self.config.default_language)
            )

            await self.event_bus.emit(Event(
                type=EventTypes.LLM_RESPONSE,
                data=response
            ))

        except Exception as e:
            logger.error(f"Error procesando con LLM: {e}")
            await self.event_bus.emit(Event(
                type=EventTypes.LLM_ERROR,
                data={"error": str(e)}
            ))

    async def _handle_stt_error(self, event: Event):
        """Handler para errores de STT."""
        error_msg = self.config.responses.error_messages.get(
            self.config.default_language,
            "Error"
        )
        audio_data = await self.tts_engine.synthesize(error_msg, self.config.default_language)
        await self.audio_manager.play(audio_data)
        self.state_machine.transition(State.IDLE)

    async def _handle_llm_response(self, event: Event):
        """Handler para respuesta del LLM."""
        response_data = event.data
        response_text = response_data.get("response", "")
        actions = response_data.get("actions", [])
        requires_confirmation = response_data.get("requires_confirmation", False)

        # Si requiere confirmación
        if requires_confirmation and actions:
            self.state_machine.transition(State.CONFIRMING)
            await self.event_bus.emit(Event(
                type=EventTypes.CONFIRMATION_REQUIRED,
                data={"actions": actions, "response": response_text}
            ))
            return

        # Si hay acciones, ejecutarlas
        if actions:
            self.state_machine.transition(State.EXECUTING)

            try:
                results = await self.action_executor.execute_actions(actions)

                await self.event_bus.emit(Event(
                    type=EventTypes.ACTION_COMPLETE,
                    data={"results": results, "response": response_text}
                ))
            except Exception as e:
                logger.error(f"Error ejecutando acciones: {e}")
                await self.event_bus.emit(Event(
                    type=EventTypes.ACTION_ERROR,
                    data={"error": str(e), "response": response_text}
                ))
        else:
            # Solo responder con TTS
            self.state_machine.transition(State.SPEAKING)
            audio_data = await self.tts_engine.synthesize(response_text, self.config.default_language)
            await self.audio_manager.play(audio_data)
            await self.event_bus.emit(Event(type=EventTypes.TTS_COMPLETE))

    async def _handle_llm_error(self, event: Event):
        """Handler para errores del LLM."""
        error_msg = self.config.responses.error_messages.get(
            self.config.default_language,
            "Error"
        )
        audio_data = await self.tts_engine.synthesize(error_msg, self.config.default_language)
        await self.audio_manager.play(audio_data)
        self.state_machine.transition(State.IDLE)

    async def _handle_confirmation_required(self, event: Event):
        """Handler para cuando se requiere confirmación."""
        actions = event.data.get("actions", [])
        response = event.data.get("response", "")

        # Pedir confirmación
        confirmation_msg = self.config.responses.confirmation_prompts.get(
            self.config.default_language,
            "Confirm?"
        )

        full_msg = f"{response}. {confirmation_msg}"
        audio_data = await self.tts_engine.synthesize(full_msg, self.config.default_language)
        await self.audio_manager.play(audio_data)

        # Capturar respuesta
        try:
            response_audio = await self.audio_manager.capture_until_silence(
                max_seconds=5.0,
                silence_threshold_seconds=1.0
            )

            if len(response_audio) > 0:
                confirmation_text, _ = await self.stt_engine.transcribe(response_audio)
                confirmed = self._parse_confirmation(confirmation_text)

                await self.event_bus.emit(Event(
                    type=EventTypes.CONFIRMATION_RECEIVED,
                    data={"confirmed": confirmed, "actions": actions}
                ))

                if confirmed:
                    self.state_machine.transition(State.EXECUTING)
                    results = await self.action_executor.execute_actions(actions)
                    await self.event_bus.emit(Event(
                        type=EventTypes.ACTION_COMPLETE,
                        data={"results": results, "response": "Done"}
                    ))
                else:
                    audio_data = await self.tts_engine.synthesize("Cancelado", self.config.default_language)
                    await self.audio_manager.play(audio_data)
                    self.state_machine.transition(State.IDLE)
            else:
                audio_data = await self.tts_engine.synthesize("No escuché respuesta", self.config.default_language)
                await self.audio_manager.play(audio_data)
                self.state_machine.transition(State.IDLE)

        except Exception as e:
            logger.error(f"Error en confirmación: {e}")
            self.state_machine.transition(State.IDLE)

    def _parse_confirmation(self, text: str) -> bool:
        """Parsea texto de confirmación."""
        text_lower = text.lower().strip()

        # Español
        affirmative_es = ["sí", "si", "confirmo", "adelante", "ok", "vale", "claro", "afirmativo"]
        # Inglés
        affirmative_en = ["yes", "confirm", "ok", "sure", "affirmative", "go ahead"]

        return any(word in text_lower for word in affirmative_es + affirmative_en)

    async def _handle_action_complete(self, event: Event):
        """Handler para acciones completadas."""
        response = event.data.get("response", "Hecho")

        self.state_machine.transition(State.SPEAKING)
        audio_data = await self.tts_engine.synthesize(response, self.config.default_language)
        await self.audio_manager.play(audio_data)
        await self.event_bus.emit(Event(type=EventTypes.TTS_COMPLETE))

    async def _handle_action_error(self, event: Event):
        """Handler para errores en acciones."""
        error_msg = self.config.responses.error_messages.get(
            self.config.default_language,
            "Error"
        )

        self.state_machine.transition(State.SPEAKING)
        audio_data = await self.tts_engine.synthesize(error_msg, self.config.default_language)
        await self.audio_manager.play(audio_data)
        await self.event_bus.emit(Event(type=EventTypes.TTS_COMPLETE))

    async def _handle_tts_complete(self, event: Event):
        """Handler para TTS completado."""
        self.state_machine.transition(State.IDLE)

    async def run(self):
        """Loop principal del asistente."""
        logger.info("=== Home-Alexa iniciado ===")
        logger.info(f"Escuchando wake word: '{self.config.wakeword.phrase}'")

        self._running = True

        # Iniciar captura de audio
        await self.audio_manager.start_capture()

        # Emitir evento de sistema listo
        await self.event_bus.emit(Event(type=EventTypes.SYSTEM_READY))

        try:
            # Loop de detección de wake word
            async for chunk in self.audio_manager.stream():
                if not self._running:
                    break

                # Solo detectar wake word si está IDLE
                if self.state_machine.is_idle:
                    detected = await self.wakeword_detector.process(chunk)

                    if detected:
                        await self.event_bus.emit(Event(
                            type=EventTypes.WAKE_DETECTED,
                            data={"timestamp": asyncio.get_event_loop().time()}
                        ))

                        # Cooldown para evitar múltiples detecciones
                        await asyncio.sleep(self.config.wakeword.cooldown_seconds)

        except asyncio.CancelledError:
            logger.info("Loop principal cancelado")
        except Exception as e:
            logger.error(f"Error en loop principal: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Cierra todos los componentes."""
        if not self._running:
            return

        logger.info("=== Cerrando Home-Alexa ===")
        self._running = False

        # Emitir evento de shutdown
        await self.event_bus.emit(Event(type=EventTypes.SYSTEM_SHUTDOWN))

        # Cerrar componentes
        try:
            if self.audio_manager:
                await self.audio_manager.close()
        except Exception as e:
            logger.error(f"Error cerrando audio_manager: {e}")

        try:
            if self.llm_client:
                await self.llm_client.close()
        except Exception as e:
            logger.error(f"Error cerrando llm_client: {e}")

        try:
            if self.memory_manager:
                await self.memory_manager.close()
        except Exception as e:
            logger.error(f"Error cerrando memory_manager: {e}")

        try:
            if self.event_bus:
                await self.event_bus.stop_processor()
        except Exception as e:
            logger.error(f"Error cerrando event_bus: {e}")

        logger.info("=== Sistema cerrado ===")
        self._shutdown_event.set()


async def main():
    """Función principal."""
    alexa = HomeAlexa()

    # Configurar señales para shutdown graceful
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("Señal de interrupción recibida")
        asyncio.create_task(alexa.shutdown())

    # Registrar manejadores de señales
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        # Inicializar
        await alexa.initialize()

        # Ejecutar
        await alexa.run()

        # Esperar shutdown
        await alexa._shutdown_event.wait()

    except KeyboardInterrupt:
        logger.info("Interrupción por teclado")
        await alexa.shutdown()
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        await alexa.shutdown()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Saliendo...")
