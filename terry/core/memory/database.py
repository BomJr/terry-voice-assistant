"""
Home-Alexa - Database
Gestión de la base de datos SQLite
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import threading

from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


# Schema SQL para crear las tablas
SCHEMA_SQL = """
-- Tabla principal de conversaciones
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    transcription TEXT NOT NULL,
    intent TEXT,
    response TEXT,
    language TEXT DEFAULT 'es',
    audio_duration REAL,
    processing_time REAL,
    is_important BOOLEAN DEFAULT FALSE,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_expires ON conversations(expires_at);

-- Tabla de acciones ejecutadas
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    params TEXT,
    result TEXT,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_actions_conversation ON actions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(action_type);

-- Preferencias del usuario
CREATE TABLE IF NOT EXISTS user_prefs (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insertar preferencias por defecto
INSERT OR IGNORE INTO user_prefs (key, value) VALUES
    ('default_language', 'es'),
    ('voice_speed', '1.0'),
    ('confirmation_level', 'critical'),
    ('default_browser', 'Atlas'),
    ('volume_step', '10');

-- Hechos memorizados (memoria a largo plazo)
CREATE TABLE IF NOT EXISTS memory_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact TEXT NOT NULL,
    category TEXT,
    importance INTEGER DEFAULT 5,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME,
    access_count INTEGER DEFAULT 0,
    expires_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_facts_category ON memory_facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_importance ON memory_facts(importance DESC);

-- Recordatorios
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    trigger_at DATETIME NOT NULL,
    repeat TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reminders_trigger ON reminders(trigger_at);

-- Alarmas
CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TIME NOT NULL,
    days TEXT DEFAULT '1,2,3,4,5,6,7',
    label TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    sound TEXT DEFAULT 'default',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Logs del sistema
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,
    module TEXT,
    message TEXT NOT NULL,
    is_critical BOOLEAN DEFAULT FALSE,
    expires_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_expires ON logs(expires_at);

-- Trigger para establecer expiración de logs
CREATE TRIGGER IF NOT EXISTS set_log_expiration
AFTER INSERT ON logs
BEGIN
    UPDATE logs
    SET expires_at = CASE
        WHEN NEW.is_critical = 1 THEN NULL
        ELSE datetime(NEW.timestamp, '+24 hours')
    END
    WHERE id = NEW.id;
END;

-- Trigger para establecer expiración de conversaciones
CREATE TRIGGER IF NOT EXISTS set_conversation_expiration
AFTER INSERT ON conversations
BEGIN
    UPDATE conversations
    SET expires_at = CASE
        WHEN NEW.is_important = 1 THEN NULL
        ELSE datetime(NEW.timestamp, '+7 days')
    END
    WHERE id = NEW.id;
END;
"""


class Database:
    """Gestión de la base de datos SQLite."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._initialized = False

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión thread-local."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
            # Habilitar foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection

    @contextmanager
    def get_cursor(self):
        """Context manager para obtener un cursor."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    async def initialize(self) -> None:
        """Inicializa la base de datos."""
        # Crear directorio si no existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear tablas
        await asyncio.get_event_loop().run_in_executor(
            None,
            self._create_tables
        )
        self._initialized = True
        logger.info(f"Base de datos inicializada: {self.db_path}")

    def _create_tables(self) -> None:
        """Crea las tablas en la base de datos."""
        with self.get_cursor() as cursor:
            cursor.executescript(SCHEMA_SQL)

    async def execute(
        self,
        query: str,
        params: tuple = ()
    ) -> Optional[int]:
        """
        Ejecuta una query y retorna el lastrowid.

        Args:
            query: Query SQL
            params: Parámetros de la query

        Returns:
            lastrowid si aplica
        """
        def _execute():
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid

        return await asyncio.get_event_loop().run_in_executor(None, _execute)

    async def execute_many(
        self,
        query: str,
        params_list: List[tuple]
    ) -> None:
        """
        Ejecuta una query múltiples veces.

        Args:
            query: Query SQL
            params_list: Lista de tuplas de parámetros
        """
        def _execute_many():
            with self.get_cursor() as cursor:
                cursor.executemany(query, params_list)

        await asyncio.get_event_loop().run_in_executor(None, _execute_many)

    async def fetch_one(
        self,
        query: str,
        params: tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Ejecuta query y retorna una fila.

        Args:
            query: Query SQL
            params: Parámetros

        Returns:
            Diccionario con la fila o None
        """
        def _fetch():
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

        return await asyncio.get_event_loop().run_in_executor(None, _fetch)

    async def fetch_all(
        self,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta query y retorna todas las filas.

        Args:
            query: Query SQL
            params: Parámetros

        Returns:
            Lista de diccionarios
        """
        def _fetch():
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        return await asyncio.get_event_loop().run_in_executor(None, _fetch)

    async def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
        logger.info("Base de datos cerrada")

    @property
    def is_initialized(self) -> bool:
        """Verifica si la BD está inicializada."""
        return self._initialized
