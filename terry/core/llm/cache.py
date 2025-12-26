"""
Home-Alexa - Caché de Respuestas Rápidas
Para comandos comunes, responde directo sin llamar al LLM
"""

from typing import Optional, Dict, Any
import re
from terry.core.utils.fuzzy_matcher import get_fuzzy_matcher


class ResponseCache:
    """Caché de respuestas para comandos comunes."""

    # Patrones de comandos comunes → respuestas directas
    QUICK_RESPONSES = {
        # Abrir apps
        r"abr[ei]\s+(safari|chrome|firefox|music|notes|calculator|mail)": {
            "intent": "open_app",
            "action_type": "open_app",
            "response": "Abriendo {app}"
        },

        # Volumen
        r"sube?(?:\s+el)?\s+volumen": {
            "intent": "volume_up",
            "action_type": "volume_up",
            "response": "Subiendo volumen",
            "params": {"amount": 10}
        },
        r"baj[ae](?:\s+el)?\s+volumen": {
            "intent": "volume_down",
            "action_type": "volume_down",
            "response": "Bajando volumen",
            "params": {"amount": 10}
        },
        r"silencia|mute": {
            "intent": "volume_mute",
            "action_type": "volume_mute",
            "response": "Silenciando",
            "params": {}
        },

        # Multimedia - PLAY (muchas variaciones)
        r"(?:pon|reproduce?|play|continua|reanuda|sigue|dale|arranca|inicia|activa|prende|despausa)\s+(?:la\s+|el\s+)?(?:m[uú]sica|video|canci[oó]n|tema|audio|sonido)": {
            "intent": "media_play",
            "action_type": "media_play",
            "response": "Reproduciendo",
            "params": {}
        },
        r"^(?:pon|reproduce?|play|continua|reanuda|sigue|dale)$": {
            "intent": "media_play",
            "action_type": "media_play",
            "response": "Reproduciendo",
            "params": {}
        },

        # Multimedia - PAUSE (muchas variaciones)
        r"(?:para|pausa|pause|det[eé]n|para?|frena|apaga|corta|silencia|stop)\s+(?:la\s+|el\s+)?(?:m[uú]sica|video|canci[oó]n|tema|audio|sonido)": {
            "intent": "media_pause",
            "action_type": "media_pause",
            "response": "Pausando",
            "params": {}
        },
        r"^(?:para|pausa|pause|det[eé]n|stop|apaga)$": {
            "intent": "media_pause",
            "action_type": "media_pause",
            "response": "Pausando",
            "params": {}
        },
        # Multimedia - SIGUIENTE (muchas variaciones)
        r"(?:siguiente|next|pr[oó]xima?|adelante|salta|skip|cambia|avanza)\s+(?:canci[oó]n|video|pista|track|tema)": {
            "intent": "media_next",
            "action_type": "media_next",
            "response": "Siguiente",
            "params": {}
        },
        r"^(?:siguiente|next|pr[oó]xima?|adelante|salta|skip)$": {
            "intent": "media_next",
            "action_type": "media_next",
            "response": "Siguiente",
            "params": {}
        },

        # Multimedia - ANTERIOR (muchas variaciones)
        r"(?:anterior|previous|atr[aá]s|vuelve|retrocede|back)\s+(?:canci[oó]n|video|pista|track|tema)": {
            "intent": "media_previous",
            "action_type": "media_previous",
            "response": "Anterior",
            "params": {}
        },
        r"^(?:anterior|previous|atr[aá]s|vuelve|retrocede)$": {
            "intent": "media_previous",
            "action_type": "media_previous",
            "response": "Anterior",
            "params": {}
        },

        # Búsquedas web
        r"busca(?:\s+en\s+google)?\s+(.+)": {
            "intent": "web_search",
            "action_type": "browser_search",
            "response": "Buscando {query}",
            "extract": "query"
        },

        # URLs
        r"abr[ei]\s+(https?://\S+|www\.\S+|\S+\.com)": {
            "intent": "open_url",
            "action_type": "browser_open_url",
            "response": "Abriendo {url}",
            "extract": "url"
        },

        # Now Playing - Qué está sonando
        r"(?:qu[eé]|que)\s+(?:suena|est[aá]\s+sonando|canción|canci[oó]n\s+(?:est[aá]|es)|reproduciendo|música|musica)": {
            "intent": "now_playing",
            "action_type": "now_playing",
            "response": "Obteniendo canción actual",
            "params": {}
        },
        r"^(?:now\s+playing|what'?s?\s+playing)$": {
            "intent": "now_playing",
            "action_type": "now_playing",
            "response": "Obteniendo canción actual",
            "params": {}
        },

        # Conversación y Saludos
        r"^(hola|hey|hi|hello|buenos d[ií]as|buenas tardes|buenas noches|qu[eé] tal)": {
            "intent": "greeting",
            "action_type": "no_action",
            "response": "¡Hola! ¿En qué puedo ayudarte hoy?",
            "params": {}
        },
        r"^(gracias|thank you|thanks|muchas gracias)": {
            "intent": "thanks",
            "action_type": "no_action",
            "response": "¡De nada! Cuando necesites algo, aquí estoy.",
            "params": {}
        },
        r"^(adi[oó]s|chao|bye|hasta luego|nos vemos)": {
            "intent": "goodbye",
            "action_type": "no_action",
            "response": "¡Hasta pronto!",
            "params": {}
        },

        # Preguntas sobre Terry
        r"^(c[oó]mo te llamas?|qui[eé]n eres?|qu[eé] eres?)": {
            "intent": "about_terry",
            "action_type": "no_action",
            "response": "Soy Terry, tu asistente de voz personal. ¿En qué te puedo ayudar?",
            "params": {}
        },
        r"^(qu[eé] puedes hacer|qu[eé] sabes hacer|ayuda|help)": {
            "intent": "help",
            "action_type": "no_action",
            "response": "Puedo controlar música, abrir apps, buscar en internet, y mucho más. Solo dime qué necesitas.",
            "params": {}
        },

        # Rutinas por voz (v6.0)
        r"(?:modo|rutina|activa|activar)\s+(trabajo|focus|descanso|noche|buenas?\s+noches?|buenos?\s+d[ií]as?)": {
            "intent": "activate_routine",
            "action_type": "routine",  # Manejo especial en command_processor
            "response": "Activando rutina {routine_name}",
            "extract": "routine_name"
        },

        # Gestos de voz rápidos (v6.0)
        r"^(ok|okay|vale|s[ií])$": {
            "intent": "gesture_ok",
            "action_type": "gesture_ok",  # Manejo especial en command_processor
            "response": "",  # Determinado por contexto
            "params": {"gesture": "ok"}
        },
        r"^(mmm|mmmm|repite|otra vez|de nuevo|repeat)$": {
            "intent": "repeat_response",
            "action_type": "no_action",
            "response": "{last_response}",  # Reemplazado dinámicamente
            "params": {"gesture": "repeat"}
        },
        r"^(qu[eé]\??|c[oó]mo\??|what\??|perdona?\??|perd[oó]n\??)$": {
            "intent": "repeat_command",
            "action_type": "no_action",
            "response": "Dijiste: {last_command}",
            "params": {"gesture": "what"}
        },
        r"^(cancela|cancel|para eso|d[eé]jalo|forget it|stop|alto)$": {
            "intent": "cancel",
            "action_type": "cancel_action",
            "response": "Cancelado",
            "params": {"gesture": "cancel"}
        },

        # Voice Notes (v6.1) - Note-taking with semantic search
        r"(?:terry\s+)?nota:?\s+(.+)": {
            "intent": "add_note",
            "action_type": "voice_notes",
            "response": "Nota guardada",
            "extract": "content",
            "params": {"action": "add"}
        },
        r"(?:terry\s+)?(?:apunta|anota|recuerda|guarda)\s+(?:que|esto:?)?\s*(.+)": {
            "intent": "add_note",
            "action_type": "voice_notes",
            "response": "Anotado",
            "extract": "content",
            "params": {"action": "add"}
        },
        r"(?:busca|encuentra|muestra|lista)\s+(?:mis\s+)?notas?\s+(?:sobre|de|con)\s+(.+)": {
            "intent": "search_notes",
            "action_type": "voice_notes",
            "response": "Buscando notas sobre {query}",
            "extract": "query",
            "params": {"action": "search"}
        },
        r"^(?:mis\s+)?(?:[uú]ltimas\s+)?notas?(?:\s+pendientes?)?$": {
            "intent": "list_notes",
            "action_type": "voice_notes",
            "response": "Mostrando tus notas",
            "params": {"action": "list"}
        },
        r"(?:completa|marca)\s+(?:la\s+)?(?:[uú]ltima\s+)?nota": {
            "intent": "complete_note",
            "action_type": "voice_notes",
            "response": "Nota completada",
            "params": {"action": "complete"}
        },

        # Camera Vision (v6.1) - Face recognition and presence detection
        r"(?:qui[eé]n\s+(?:est[aá]|hay)|hay\s+alguien)\s+(?:aqu[ií]|ah[ií]|presente|en\s+pantalla)": {
            "intent": "who_is_here",
            "action_type": "camera",
            "response": "Verificando quién está presente",
            "params": {"action": "who_is_here"}
        },
        r"(?:est[aá]|se\s+encuentra)\s+(.+?)\s+(?:aqu[ií]|presente|en\s+pantalla)": {
            "intent": "is_person_present",
            "action_type": "camera",
            "response": "Verificando si {name} está presente",
            "extract": "name",
            "params": {"action": "is_present"}
        },
        r"(?:activa|inicia|enciende|arranca)\s+(?:la\s+)?c[aá]mara": {
            "intent": "camera_start",
            "action_type": "camera",
            "response": "Activando cámara",
            "params": {"action": "start"}
        },
        r"(?:desactiva|det[eé]n|apaga|para)\s+(?:la\s+)?c[aá]mara": {
            "intent": "camera_stop",
            "action_type": "camera",
            "response": "Deteniendo cámara",
            "params": {"action": "stop"}
        },
        r"(?:estado|status)\s+(?:de\s+)?(?:la\s+)?c[aá]mara": {
            "intent": "camera_status",
            "action_type": "camera",
            "response": "Verificando estado de la cámara",
            "params": {"action": "status"}
        },
        r"(?:estad[ií]sticas|stats)\s+(?:de\s+)?(?:la\s+)?c[aá]mara": {
            "intent": "camera_stats",
            "action_type": "camera",
            "response": "Obteniendo estadísticas",
            "params": {"action": "stats"}
        },
        r"(?:borra|elimina)\s+(?:la\s+)?nota\s+(\d+)": {
            "intent": "delete_note",
            "action_type": "voice_notes",
            "response": "Nota eliminada",
            "extract": "note_id",
            "params": {"action": "delete"}
        },

        # Undo System (v6.1) - Undo last action
        r"^(?:deshaz|deshacer|undo|vuelve\s+atr[aá]s|revertir|cancelar?\s+[uú]ltim[ao])": {
            "intent": "undo",
            "action_type": "undo",
            "response": "Deshaciendo...",
            "params": {}
        },

        # Camera Vision (v6.1) - Face recognition and screen analysis
        r"(?:qui[ée]n\s+(?:est[aá]|hay|veo)|reconoce\s+(?:esta\s+)?persona|(?:who|recognize)\s+(?:is|this))": {
            "intent": "recognize_person",
            "action_type": "camera_vision",
            "response": "Analizando...",
            "params": {"action": "recognize"}
        },
        r"(?:captura|toma)\s+(?:la\s+)?pantalla|screenshot|screen\s+capture": {
            "intent": "screenshot",
            "action_type": "camera_vision",
            "response": "Capturando pantalla...",
            "params": {"action": "screenshot"}
        },
        r"(?:qu[ée]\s+(?:hay|veo|ves)\s+en\s+(?:la\s+)?pantalla|describe\s+(?:la\s+)?pantalla|what(?:'s|\s+is)\s+on\s+(?:the\s+)?screen)": {
            "intent": "describe_screen",
            "action_type": "camera_vision",
            "response": "Analizando pantalla...",
            "params": {"action": "describe_screen"}
        },
        r"(?:estad[ií]sticas|stats)\s+(?:de\s+)?(?:reconocimiento|vision|face)": {
            "intent": "vision_stats",
            "action_type": "camera_vision",
            "response": "Obteniendo estadísticas...",
            "params": {"action": "stats"}
        },

        # OCR Universal (v6.1) - Text extraction from screen
        r"(?:lee|leer)\s+(?:la\s+)?(?:pantalla|texto|esto)|read\s+(?:the\s+)?(?:screen|text)": {
            "intent": "ocr_read",
            "action_type": "ocr",
            "response": "Leyendo pantalla...",
            "params": {"action": "read"}
        },
        r"(?:copia|copiar)\s+(?:el\s+)?texto\s+(?:de\s+(?:la\s+)?pantalla)?|copy\s+text\s+from\s+screen": {
            "intent": "ocr_copy",
            "action_type": "ocr",
            "response": "Copiando texto...",
            "params": {"action": "copy"}
        },
        r"(?:extrae|extraer)\s+texto\s+de\s+(.+)|extract\s+text\s+from\s+(.+)": {
            "intent": "ocr_extract",
            "action_type": "ocr",
            "response": "Extrayendo texto...",
            "extract": "image_path",
            "params": {"action": "extract"}
        },

        # Scheduled Routines (v6.1) - Cron-style scheduling
        r"(?:programa|schedule)\s+(?:rutina|routine)": {
            "intent": "schedule_add",
            "action_type": "scheduler",
            "response": "Programando rutina...",
            "params": {"action": "add"}
        },
        r"(?:lista|list)\s+(?:rutinas|routines)": {
            "intent": "schedule_list",
            "action_type": "scheduler",
            "response": "Listando rutinas...",
            "params": {"action": "list"}
        },
        r"(?:elimina|borra|remove|delete)\s+rutina": {
            "intent": "schedule_remove",
            "action_type": "scheduler",
            "response": "Eliminando rutina...",
            "params": {"action": "remove"}
        },
        r"(?:activa|enable)\s+rutina": {
            "intent": "schedule_enable",
            "action_type": "scheduler",
            "response": "Activando rutina...",
            "params": {"action": "enable"}
        },
        r"(?:desactiva|disable)\s+rutina": {
            "intent": "schedule_disable",
            "action_type": "scheduler",
            "response": "Desactivando rutina...",
            "params": {"action": "disable"}
        },

        # Conditional Triggers (v6.1) - IFTTT-style automation
        r"(?:si\s+abro|cuando\s+abra|if\s+(?:i\s+)?open)\s+(.+?)\s+(?:entonces\s+)?(.+)": {
            "intent": "trigger_app_open",
            "action_type": "triggers",
            "response": "Trigger creado",
            "params": {
                "action": "add",
                "condition_type": "app_open",
                "condition_params": {"app_name": "$1"},
                "action_command": "$2"
            }
        },
        r"(?:lista|list)\s+(?:los\s+)?triggers": {
            "intent": "trigger_list",
            "action_type": "triggers",
            "response": "Listando triggers...",
            "params": {"action": "list"}
        },
        r"(?:elimina|borra|remove|delete)\s+trigger": {
            "intent": "trigger_remove",
            "action_type": "triggers",
            "response": "Eliminando trigger...",
            "params": {"action": "remove"}
        },

        # Macro Recording (v6.1) - Record and replay command sequences
        r"(?:graba|record)\s+macro\s+(.+)": {
            "intent": "macro_start",
            "action_type": "macros",
            "response": "Iniciando grabación...",
            "extract": "name",
            "params": {"action": "start_recording"}
        },
        r"(?:det[ée]n|stop|termina)\s+(?:la\s+)?grabaci[óo]n": {
            "intent": "macro_stop",
            "action_type": "macros",
            "response": "Deteniendo grabación...",
            "params": {"action": "stop_recording"}
        },
        r"(?:cancela|cancel)\s+(?:la\s+)?grabaci[óo]n": {
            "intent": "macro_cancel",
            "action_type": "macros",
            "response": "Cancelando grabación...",
            "params": {"action": "cancel_recording"}
        },
        r"(?:ejecuta|run|play)\s+macro\s+(.+)": {
            "intent": "macro_execute",
            "action_type": "macros",
            "response": "Ejecutando macro...",
            "extract": "name",
            "params": {"action": "execute"}
        },
        r"(?:lista|list)\s+(?:los\s+)?macros": {
            "intent": "macro_list",
            "action_type": "macros",
            "response": "Listando macros...",
            "params": {"action": "list"}
        },
        r"(?:elimina|borra|delete)\s+macro\s+(.+)": {
            "intent": "macro_delete",
            "action_type": "macros",
            "response": "Eliminando macro...",
            "extract": "name",
            "params": {"action": "delete"}
        },

        # Universal Dictation (v6.1) - Type to active application
        r"(?:escribe|dicta|type)\s+(.+)": {
            "intent": "dictate_text",
            "action_type": "dictation",
            "response": "Dictando...",
            "extract": "text",
            "params": {"action": "type"}
        },
        r"(?:inicia|empieza|start)\s+dictado": {
            "intent": "dictation_start",
            "action_type": "dictation",
            "response": "Iniciando modo dictado...",
            "params": {"action": "start"}
        },
        r"(?:fin|termina|stop)\s+dictado": {
            "intent": "dictation_stop",
            "action_type": "dictation",
            "response": "Terminando dictado...",
            "params": {"action": "stop"}
        },
        r"(?:borra|elimina|delete)\s+(?:la\s+)?(?:última\s+)?palabra": {
            "intent": "dictation_delete_word",
            "action_type": "dictation",
            "response": "Borrando palabra...",
            "params": {"action": "delete_word"}
        },
        r"nueva\s+l[íi]nea|new\s+line": {
            "intent": "dictation_newline",
            "action_type": "dictation",
            "response": "Nueva línea",
            "params": {"action": "new_line"}
        },
        r"nuevo\s+p[áa]rrafo|new\s+paragraph": {
            "intent": "dictation_paragraph",
            "action_type": "dictation",
            "response": "Nuevo párrafo",
            "params": {"action": "new_paragraph"}
        },

        # File Search (v6.1) - Spotlight-based file search
        r"(?:busca|encuentra|search|find)\s+(?:el\s+)?archivo\s+(.+)": {
            "intent": "search_file",
            "action_type": "file_search",
            "response": "Buscando archivo...",
            "extract": "query",
            "params": {"action": "search"}
        },
        r"(?:busca|search)\s+archivos?\s+(?:que\s+)?(?:contengan|con|containing)\s+(.+)": {
            "intent": "search_content",
            "action_type": "file_search",
            "response": "Buscando contenido...",
            "extract": "query",
            "params": {"action": "search_content"}
        },
        r"abre\s+(?:el\s+)?archivo\s+(.+)": {
            "intent": "open_file",
            "action_type": "file_search",
            "response": "Abriendo archivo...",
            "extract": "file_path",
            "params": {"action": "open"}
        },

        # IDE Control (v6.1) - VS Code control
        r"(?:ejecuta|run)\s+(?:los\s+)?tests?": {
            "intent": "ide_run_tests",
            "action_type": "ide_control",
            "response": "Ejecutando tests...",
            "params": {"action": "run_tests"}
        },
        r"git\s+status": {
            "intent": "ide_git_status",
            "action_type": "ide_control",
            "response": "Mostrando git status...",
            "params": {"action": "git_status"}
        },
        r"git\s+commit\s+(.+)": {
            "intent": "ide_git_commit",
            "action_type": "ide_control",
            "response": "Haciendo commit...",
            "extract": "message",
            "params": {"action": "git_commit"}
        },
        r"git\s+push": {
            "intent": "ide_git_push",
            "action_type": "ide_control",
            "response": "Pushing...",
            "params": {"action": "git_push"}
        },
    }

    @classmethod
    def get_quick_response(cls, user_input: str, session_state=None) -> Optional[Dict[str, Any]]:
        """
        Intenta obtener una respuesta rápida del caché.
        Ahora con tolerancia a faltas de ortografía y gestos de voz (v6.0)!

        Args:
            user_input: Texto del usuario
            session_state: Estado de sesión para gestos context-aware

        Returns:
            Dict con la respuesta o None si no hay match
        """
        # PASO 1: Normalizar con fuzzy matcher (corrige errores comunes)
        fuzzy = get_fuzzy_matcher()
        text = fuzzy.normalize_text(user_input)

        # PASO 2: Intentar match exacto (con texto normalizado)
        for pattern, template in cls.QUICK_RESPONSES.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Construir respuesta
                response_text = template["response"]

                # Manejar gestos con placeholders (v6.0)
                if "{last_response}" in response_text and session_state:
                    response_text = response_text.format(
                        last_response=session_state.last_response_text or "No recuerdo mi última respuesta"
                    )
                if "{last_command}" in response_text and session_state:
                    response_text = response_text.format(
                        last_command=session_state.last_command_text or "No recuerdo tu último comando"
                    )

                response = {
                    "intent": template["intent"],
                    "actions": [],
                    "response": response_text,
                    "requires_confirmation": False,
                    "language": "es",
                    "cached": True  # Marcar como cacheada
                }

                # Construir acción
                action = {
                    "type": template["action_type"],
                    "params": template.get("params", {}).copy()
                }

                # Extraer parámetros del match
                if "extract" in template:
                    param_name = template["extract"]
                    if match.groups():
                        value = match.group(1).strip()
                        action["params"][param_name] = value
                        response["response"] = template["response"].format(**{param_name: value})

                # Para open_app, extraer nombre de app
                if template["action_type"] == "open_app" and match.groups():
                    app_name = match.group(1).capitalize()
                    action["params"]["app_name"] = app_name
                    response["response"] = template["response"].format(app=app_name)

                response["actions"].append(action)
                return response

        # PASO 3: Si no hay match exacto, intentar fuzzy matching
        # (solo para comandos muy similares, threshold 0.85)
        fuzzy_result = fuzzy.fuzzy_match_pattern(text, cls.QUICK_RESPONSES, threshold=0.85)

        if fuzzy_result:
            pattern, template, similarity = fuzzy_result

            # Construir respuesta (similar al código de arriba pero sin extraer parámetros complejos)
            response = {
                "intent": template["intent"],
                "actions": [{
                    "type": template["action_type"],
                    "params": template.get("params", {}).copy()
                }],
                "response": template["response"],
                "requires_confirmation": False,
                "language": "es",
                "cached": True,
                "fuzzy_matched": True,  # Indicar que fue fuzzy match
                "similarity": round(similarity, 2)
            }

            return response

        return None
