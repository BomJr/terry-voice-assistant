"""
Home-Alexa - Context Builder
Construcción de contexto para el LLM basado en memoria
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from memory.memory_manager import MemoryManager
from utils.logger import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """
    Construye el contexto para las peticiones al LLM
    basándose en la memoria del asistente.
    """

    def __init__(
        self,
        memory_manager: MemoryManager,
        context_window: int = 5
    ):
        self.memory = memory_manager
        self.context_window = context_window

    async def build(
        self,
        current_input: str,
        language: str = "es",
        include_facts: bool = True,
        include_preferences: bool = True
    ) -> str:
        """
        Construye el contexto completo para el LLM.

        Args:
            current_input: Input actual del usuario
            language: Idioma de la conversación
            include_facts: Si incluir hechos memorizados
            include_preferences: Si incluir preferencias

        Returns:
            String con el contexto formateado
        """
        context_parts = []

        # Conversaciones recientes
        recent = await self._get_conversation_context()
        if recent:
            context_parts.append(recent)

        # Hechos relevantes
        if include_facts:
            facts = await self._get_relevant_facts(current_input)
            if facts:
                context_parts.append(facts)

        # Preferencias del usuario
        if include_preferences:
            prefs = await self._get_preferences_context()
            if prefs:
                context_parts.append(prefs)

        # Información temporal
        time_context = self._get_time_context(language)
        context_parts.append(time_context)

        return "\n\n".join(context_parts)

    async def _get_conversation_context(self) -> str:
        """Obtiene el contexto de conversaciones recientes."""
        conversations = await self.memory.get_recent_conversations(
            limit=self.context_window,
            include_actions=False
        )

        if not conversations:
            return ""

        lines = ["CONVERSACIONES RECIENTES:"]
        for conv in reversed(conversations):  # Más antiguas primero
            timestamp = conv.get('timestamp', '')
            user_text = conv.get('transcription', '')
            response = conv.get('response', '')
            intent = conv.get('intent', '')

            lines.append(f"Usuario: {user_text}")
            if response:
                lines.append(f"Asistente: {response}")
            lines.append("")  # Línea en blanco entre conversaciones

        return "\n".join(lines)

    async def _get_relevant_facts(self, query: str) -> str:
        """Obtiene hechos relevantes al query actual."""
        # Buscar hechos que puedan ser relevantes
        facts = await self.memory.search_facts(query, limit=3)

        if not facts:
            # Si no hay match directo, obtener los más importantes
            facts = await self.memory.get_facts(min_importance=7, limit=3)

        if not facts:
            return ""

        lines = ["INFORMACIÓN MEMORIZADA:"]
        for fact in facts:
            lines.append(f"- {fact['fact']}")
            # Actualizar acceso
            await self.memory.update_fact_access(fact['id'])

        return "\n".join(lines)

    async def _get_preferences_context(self) -> str:
        """Obtiene el contexto de preferencias."""
        prefs = await self.memory.get_all_preferences()

        if not prefs:
            return ""

        # Solo incluir preferencias relevantes
        relevant_prefs = {
            'default_browser': 'Navegador preferido',
            'default_language': 'Idioma preferido',
            'confirmation_level': 'Nivel de confirmación'
        }

        lines = ["PREFERENCIAS DEL USUARIO:"]
        for key, label in relevant_prefs.items():
            if key in prefs:
                lines.append(f"- {label}: {prefs[key]}")

        return "\n".join(lines) if len(lines) > 1 else ""

    def _get_time_context(self, language: str = "es") -> str:
        """Obtiene el contexto temporal actual."""
        now = datetime.now()

        if language == "en":
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
            return f"CURRENT TIME: {day_names[now.weekday()]}, {now.strftime('%B %d, %Y at %I:%M %p')}"
        else:
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves",
                         "Viernes", "Sábado", "Domingo"]
            month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo",
                           "Junio", "Julio", "Agosto", "Septiembre",
                           "Octubre", "Noviembre", "Diciembre"]
            return (f"FECHA Y HORA ACTUAL: {day_names[now.weekday()]}, "
                    f"{now.day} de {month_names[now.month-1]} de {now.year} "
                    f"a las {now.strftime('%H:%M')}")

    async def build_summary(self) -> str:
        """
        Construye un resumen del estado actual del asistente.
        Útil para debugging o información del sistema.
        """
        stats = await self.memory.get_stats()

        lines = [
            "=== RESUMEN DEL ASISTENTE ===",
            f"Sesión: {self.memory.session_id}",
            f"Total conversaciones: {stats.get('total_conversations', 0)}",
            f"Conversaciones hoy: {stats.get('today_conversations', 0)}",
        ]

        # Idiomas
        languages = stats.get('languages', {})
        if languages:
            lang_str = ", ".join(f"{k}: {v}" for k, v in languages.items())
            lines.append(f"Uso por idioma: {lang_str}")

        # Acciones más usadas
        top_actions = stats.get('top_actions', [])
        if top_actions:
            lines.append("Acciones más usadas:")
            for action in top_actions[:3]:
                lines.append(f"  - {action['action_type']}: {action['count']}")

        return "\n".join(lines)

    async def extract_facts_from_conversation(
        self,
        transcription: str,
        response: str
    ) -> List[Dict[str, Any]]:
        """
        Extrae hechos potencialmente memorables de una conversación.
        TODO: Implementar con LLM para extracción más inteligente.

        Args:
            transcription: Lo que dijo el usuario
            response: Respuesta del asistente

        Returns:
            Lista de hechos extraídos
        """
        # Por ahora, solo detectar patrones simples
        facts = []

        # Patrones de información personal
        patterns = [
            ("mi nombre es", "personal"),
            ("me llamo", "personal"),
            ("trabajo en", "trabajo"),
            ("vivo en", "personal"),
            ("mi cumpleaños es", "personal"),
            ("prefiero", "preferencias"),
        ]

        text_lower = transcription.lower()
        for pattern, category in patterns:
            if pattern in text_lower:
                # Extraer la frase completa como hecho
                facts.append({
                    "fact": transcription,
                    "category": category,
                    "importance": 7,  # Información personal es importante
                    "source": "conversation"
                })
                break

        return facts
