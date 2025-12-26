"""
Home-Alexa - Cleanup Scheduler
Programación de limpieza automática de datos antiguos
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading

from memory.database import Database
from utils.logger import get_logger

logger = get_logger(__name__)


class CleanupScheduler:
    """
    Gestor de limpieza automática de datos.
    Elimina logs, conversaciones y hechos antiguos según las reglas configuradas.
    """

    def __init__(
        self,
        db_path: str,
        logs_ttl_hours: int = 24,
        conversations_ttl_days: int = 7,
        facts_unused_ttl_days: int = 30,
        check_interval_hours: int = 1
    ):
        self.db = Database(db_path)
        self.logs_ttl_hours = logs_ttl_hours
        self.conversations_ttl_days = conversations_ttl_days
        self.facts_unused_ttl_days = facts_unused_ttl_days
        self.check_interval = check_interval_hours * 3600  # Convertir a segundos

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_cleanup: Optional[datetime] = None

    def start(self) -> None:
        """Inicia el scheduler de limpieza."""
        if self._running:
            return

        self._running = True

        # Iniciar en un thread separado para no bloquear
        def run_scheduler():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._scheduler_loop())

        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()

        logger.info("Cleanup scheduler iniciado")

    async def _scheduler_loop(self) -> None:
        """Loop principal del scheduler."""
        # Ejecutar limpieza inicial
        await self.cleanup_all()

        while self._running:
            try:
                await asyncio.sleep(self.check_interval)
                if self._running:
                    await self.cleanup_all()
            except Exception as e:
                logger.error(f"Error en cleanup scheduler: {e}")

    def stop(self) -> None:
        """Detiene el scheduler."""
        self._running = False
        logger.info("Cleanup scheduler detenido")

    async def cleanup_all(self) -> Dict[str, int]:
        """
        Ejecuta todas las limpiezas.

        Returns:
            Diccionario con conteo de elementos eliminados por categoría
        """
        results = {}

        try:
            results['logs'] = await self.cleanup_logs()
            results['conversations'] = await self.cleanup_conversations()
            results['facts'] = await self.cleanup_unused_facts()

            self._last_cleanup = datetime.now()

            total = sum(results.values())
            if total > 0:
                logger.info(f"Limpieza completada: {results}")

        except Exception as e:
            logger.error(f"Error durante limpieza: {e}")

        return results

    async def cleanup_logs(self) -> int:
        """
        Elimina logs expirados.

        Returns:
            Número de logs eliminados
        """
        query = """
            DELETE FROM logs
            WHERE expires_at IS NOT NULL
            AND expires_at < datetime('now')
        """

        try:
            await self.db.execute(query)

            # Obtener conteo (aproximado, ya que SQLite no retorna affected rows fácilmente)
            count_result = await self.db.fetch_one(
                "SELECT changes() as count"
            )
            count = count_result['count'] if count_result else 0

            if count > 0:
                logger.debug(f"Logs eliminados: {count}")

            return count

        except Exception as e:
            logger.error(f"Error limpiando logs: {e}")
            return 0

    async def cleanup_conversations(self) -> int:
        """
        Elimina conversaciones expiradas no importantes.

        Returns:
            Número de conversaciones eliminadas
        """
        query = """
            DELETE FROM conversations
            WHERE expires_at IS NOT NULL
            AND expires_at < datetime('now')
            AND is_important = 0
        """

        try:
            await self.db.execute(query)

            count_result = await self.db.fetch_one(
                "SELECT changes() as count"
            )
            count = count_result['count'] if count_result else 0

            if count > 0:
                logger.info(f"Conversaciones eliminadas: {count}")

            return count

        except Exception as e:
            logger.error(f"Error limpiando conversaciones: {e}")
            return 0

    async def cleanup_unused_facts(self) -> int:
        """
        Elimina hechos no accedidos recientemente con baja importancia.

        Returns:
            Número de hechos eliminados
        """
        # Calcular fecha límite
        days_ago = f"-{self.facts_unused_ttl_days} days"

        query = """
            DELETE FROM memory_facts
            WHERE (
                last_accessed < datetime('now', ?)
                OR last_accessed IS NULL
            )
            AND importance < 5
            AND expires_at IS NULL
        """

        try:
            await self.db.execute(query, (days_ago,))

            # También eliminar hechos con expiración pasada
            await self.db.execute("""
                DELETE FROM memory_facts
                WHERE expires_at IS NOT NULL
                AND expires_at < datetime('now')
            """)

            count_result = await self.db.fetch_one(
                "SELECT changes() as count"
            )
            count = count_result['count'] if count_result else 0

            if count > 0:
                logger.info(f"Hechos eliminados: {count}")

            return count

        except Exception as e:
            logger.error(f"Error limpiando hechos: {e}")
            return 0

    async def cleanup_completed_reminders(self) -> int:
        """
        Elimina recordatorios completados antiguos.

        Returns:
            Número de recordatorios eliminados
        """
        query = """
            DELETE FROM reminders
            WHERE completed = 1
            AND trigger_at < datetime('now', '-7 days')
        """

        try:
            await self.db.execute(query)

            count_result = await self.db.fetch_one(
                "SELECT changes() as count"
            )
            return count_result['count'] if count_result else 0

        except Exception as e:
            logger.error(f"Error limpiando recordatorios: {e}")
            return 0

    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de almacenamiento.

        Returns:
            Estadísticas de uso de la BD
        """
        stats = {}

        tables = ['conversations', 'actions', 'logs', 'memory_facts', 'reminders', 'alarms']

        for table in tables:
            try:
                result = await self.db.fetch_one(
                    f"SELECT COUNT(*) as count FROM {table}"
                )
                stats[table] = result['count'] if result else 0
            except Exception:
                stats[table] = 0

        # Tamaño de la base de datos
        try:
            result = await self.db.fetch_one(
                "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
            )
            stats['db_size_bytes'] = result['size'] if result else 0
            stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024 * 1024), 2)
        except Exception:
            stats['db_size_bytes'] = 0
            stats['db_size_mb'] = 0

        stats['last_cleanup'] = self._last_cleanup.isoformat() if self._last_cleanup else None

        return stats

    async def force_cleanup(self, category: str) -> int:
        """
        Fuerza limpieza de una categoría específica.

        Args:
            category: 'logs', 'conversations', 'facts', 'reminders'

        Returns:
            Número de elementos eliminados
        """
        cleanup_methods = {
            'logs': self.cleanup_logs,
            'conversations': self.cleanup_conversations,
            'facts': self.cleanup_unused_facts,
            'reminders': self.cleanup_completed_reminders
        }

        if category not in cleanup_methods:
            logger.warning(f"Categoría de limpieza no válida: {category}")
            return 0

        return await cleanup_methods[category]()
