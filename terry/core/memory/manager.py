"""
Home-Alexa - Memory Manager
Gestión de memoria persistente del asistente
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from terry.core.memory.database import Database
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    Gestor de memoria del asistente.
    Maneja conversaciones, preferencias y hechos memorizados.
    """

    def __init__(self, db_path: str):
        self.db = Database(db_path)
        self._session_id = str(uuid.uuid4())[:8]

    async def initialize(self) -> None:
        """Inicializa el gestor de memoria."""
        await self.db.initialize()
        logger.info(f"MemoryManager inicializado. Session: {self._session_id}")

    async def close(self) -> None:
        """Cierra el gestor de memoria."""
        await self.db.close()

    # ==================== Conversaciones ====================

    async def save_conversation(
        self,
        transcription: str,
        intent: Optional[str] = None,
        response: Optional[str] = None,
        language: str = "es",
        audio_duration: Optional[float] = None,
        processing_time: Optional[float] = None,
        is_important: bool = False
    ) -> int:
        """
        Guarda una conversación.

        Returns:
            ID de la conversación guardada
        """
        query = """
            INSERT INTO conversations
            (session_id, transcription, intent, response, language,
             audio_duration, processing_time, is_important)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        conversation_id = await self.db.execute(
            query,
            (self._session_id, transcription, intent, response, language,
             audio_duration, processing_time, is_important)
        )
        logger.debug(f"Conversación guardada: {conversation_id}")
        return conversation_id

    async def save_action(
        self,
        conversation_id: int,
        action_type: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None
    ) -> int:
        """Guarda una acción ejecutada."""
        query = """
            INSERT INTO actions
            (conversation_id, action_type, params, result, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return await self.db.execute(
            query,
            (conversation_id, action_type, json.dumps(params),
             json.dumps(result), success, error_message)
        )

    async def save_interaction(
        self,
        transcription: str,
        intent: Optional[str] = None,
        response: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        language: str = "es",
        audio_duration: Optional[float] = None,
        processing_time: Optional[float] = None
    ) -> int:
        """
        Guarda una interacción completa (conversación + acciones).

        Returns:
            ID de la conversación
        """
        # Determinar si es importante basado en las acciones
        is_important = False
        if actions:
            critical_types = ["terminal_run", "file_delete", "file_move"]
            is_important = any(
                a.get("type") in critical_types for a in actions
            )

        # Guardar conversación
        conv_id = await self.save_conversation(
            transcription=transcription,
            intent=intent,
            response=response,
            language=language,
            audio_duration=audio_duration,
            processing_time=processing_time,
            is_important=is_important
        )

        # Guardar acciones
        if actions:
            for action in actions:
                await self.save_action(
                    conversation_id=conv_id,
                    action_type=action.get("type", "unknown"),
                    params=action.get("params", {}),
                    result=action.get("result", {}),
                    success=action.get("success", True),
                    error_message=action.get("error")
                )

        return conv_id

    async def get_recent_conversations(
        self,
        limit: int = 5,
        include_actions: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las conversaciones más recientes.

        Args:
            limit: Número máximo de conversaciones
            include_actions: Si incluir las acciones de cada conversación

        Returns:
            Lista de conversaciones
        """
        query = """
            SELECT * FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        """
        conversations = await self.db.fetch_all(query, (limit,))

        if include_actions:
            for conv in conversations:
                actions_query = """
                    SELECT * FROM actions
                    WHERE conversation_id = ?
                    ORDER BY executed_at
                """
                conv['actions'] = await self.db.fetch_all(
                    actions_query, (conv['id'],)
                )

        return conversations

    async def mark_important(self, conversation_id: int) -> None:
        """Marca una conversación como importante."""
        query = """
            UPDATE conversations
            SET is_important = 1, expires_at = NULL
            WHERE id = ?
        """
        await self.db.execute(query, (conversation_id,))

    # ==================== Preferencias ====================

    async def get_preference(self, key: str, default: str = "") -> str:
        """Obtiene una preferencia."""
        query = "SELECT value FROM user_prefs WHERE key = ?"
        result = await self.db.fetch_one(query, (key,))
        return result['value'] if result else default

    async def set_preference(self, key: str, value: str) -> None:
        """Establece una preferencia."""
        query = """
            INSERT OR REPLACE INTO user_prefs (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        """
        await self.db.execute(query, (key, value))

    async def get_all_preferences(self) -> Dict[str, str]:
        """Obtiene todas las preferencias."""
        query = "SELECT key, value FROM user_prefs"
        rows = await self.db.fetch_all(query)
        return {row['key']: row['value'] for row in rows}

    # ==================== Hechos memorizados ====================

    async def add_fact(
        self,
        fact: str,
        category: Optional[str] = None,
        importance: int = 5,
        source: Optional[str] = None
    ) -> int:
        """
        Añade un hecho a la memoria.

        Args:
            fact: El hecho a memorizar
            category: Categoría (personal, trabajo, etc.)
            importance: Importancia 1-10
            source: Fuente del hecho

        Returns:
            ID del hecho
        """
        query = """
            INSERT INTO memory_facts (fact, category, importance, source)
            VALUES (?, ?, ?, ?)
        """
        return await self.db.execute(query, (fact, category, importance, source))

    async def get_facts(
        self,
        category: Optional[str] = None,
        min_importance: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obtiene hechos memorizados.

        Args:
            category: Filtrar por categoría
            min_importance: Importancia mínima
            limit: Máximo de resultados

        Returns:
            Lista de hechos
        """
        if category:
            query = """
                SELECT * FROM memory_facts
                WHERE category = ? AND importance >= ?
                ORDER BY importance DESC, last_accessed DESC
                LIMIT ?
            """
            return await self.db.fetch_all(query, (category, min_importance, limit))
        else:
            query = """
                SELECT * FROM memory_facts
                WHERE importance >= ?
                ORDER BY importance DESC, last_accessed DESC
                LIMIT ?
            """
            return await self.db.fetch_all(query, (min_importance, limit))

    async def update_fact_access(self, fact_id: int) -> None:
        """Actualiza el último acceso de un hecho."""
        query = """
            UPDATE memory_facts
            SET last_accessed = datetime('now'), access_count = access_count + 1
            WHERE id = ?
        """
        await self.db.execute(query, (fact_id,))

    async def search_facts(self, query_text: str, limit: int = 5) -> List[Dict]:
        """Busca hechos que contengan el texto."""
        query = """
            SELECT * FROM memory_facts
            WHERE fact LIKE ?
            ORDER BY importance DESC
            LIMIT ?
        """
        return await self.db.fetch_all(query, (f"%{query_text}%", limit))

    # ==================== Recordatorios y Alarmas ====================

    async def add_reminder(
        self,
        text: str,
        trigger_at: datetime,
        repeat: Optional[str] = None
    ) -> int:
        """Añade un recordatorio."""
        query = """
            INSERT INTO reminders (text, trigger_at, repeat)
            VALUES (?, ?, ?)
        """
        return await self.db.execute(
            query,
            (text, trigger_at.isoformat(), repeat)
        )

    async def get_pending_reminders(self) -> List[Dict]:
        """Obtiene recordatorios pendientes."""
        query = """
            SELECT * FROM reminders
            WHERE completed = 0 AND trigger_at <= datetime('now')
            ORDER BY trigger_at
        """
        return await self.db.fetch_all(query)

    async def complete_reminder(self, reminder_id: int) -> None:
        """Marca un recordatorio como completado."""
        query = "UPDATE reminders SET completed = 1 WHERE id = ?"
        await self.db.execute(query, (reminder_id,))

    async def add_alarm(
        self,
        time: str,
        days: str = "1,2,3,4,5,6,7",
        label: Optional[str] = None
    ) -> int:
        """Añade una alarma."""
        query = """
            INSERT INTO alarms (time, days, label)
            VALUES (?, ?, ?)
        """
        return await self.db.execute(query, (time, days, label))

    async def get_active_alarms(self) -> List[Dict]:
        """Obtiene alarmas activas."""
        query = "SELECT * FROM alarms WHERE enabled = 1 ORDER BY time"
        return await self.db.fetch_all(query)

    async def toggle_alarm(self, alarm_id: int, enabled: bool) -> None:
        """Activa/desactiva una alarma."""
        query = "UPDATE alarms SET enabled = ? WHERE id = ?"
        await self.db.execute(query, (enabled, alarm_id))

    # ==================== Estadísticas ====================

    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso."""
        stats = {}

        # Total de conversaciones
        result = await self.db.fetch_one(
            "SELECT COUNT(*) as count FROM conversations"
        )
        stats['total_conversations'] = result['count'] if result else 0

        # Conversaciones de hoy
        result = await self.db.fetch_one(
            "SELECT COUNT(*) as count FROM conversations WHERE date(timestamp) = date('now')"
        )
        stats['today_conversations'] = result['count'] if result else 0

        # Acciones más usadas
        result = await self.db.fetch_all("""
            SELECT action_type, COUNT(*) as count
            FROM actions
            GROUP BY action_type
            ORDER BY count DESC
            LIMIT 5
        """)
        stats['top_actions'] = result

        # Idiomas usados
        result = await self.db.fetch_all("""
            SELECT language, COUNT(*) as count
            FROM conversations
            GROUP BY language
        """)
        stats['languages'] = {r['language']: r['count'] for r in result}

        return stats

    @property
    def session_id(self) -> str:
        """ID de la sesión actual."""
        return self._session_id
