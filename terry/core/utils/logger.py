"""
Home-Alexa - Sistema de Logging
Logger configurado con rotación y auto-limpieza
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from logging.handlers import RotatingFileHandler
import threading
import time


class LogCleaner(threading.Thread):
    """Thread que limpia logs antiguos periódicamente."""

    def __init__(self, log_dir: Path, max_age_hours: int = 24, check_interval: int = 3600):
        super().__init__(daemon=True)
        self.log_dir = log_dir
        self.max_age_hours = max_age_hours
        self.check_interval = check_interval
        self.running = True

    def run(self):
        while self.running:
            self._cleanup_old_logs()
            time.sleep(self.check_interval)

    def _cleanup_old_logs(self):
        """Elimina logs más antiguos que max_age_hours."""
        if not self.log_dir.exists():
            return

        cutoff = datetime.now() - timedelta(hours=self.max_age_hours)

        for log_file in self.log_dir.glob("*.log*"):
            try:
                # No eliminar el archivo de log crítico
                if "critical" in log_file.name.lower():
                    continue

                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    log_file.unlink()
            except Exception:
                pass

    def stop(self):
        self.running = False


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para la consola."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarillo
        'ERROR': '\033[31m',     # Rojo
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


_log_cleaner: Optional[LogCleaner] = None
_loggers: dict = {}


def setup_logger(
    log_dir: Optional[Path] = None,
    level: str = "INFO",
    auto_cleanup: bool = True,
    max_age_hours: int = 24
) -> logging.Logger:
    """
    Configura el sistema de logging global.

    Args:
        log_dir: Directorio para archivos de log
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        auto_cleanup: Si activar limpieza automática de logs antiguos
        max_age_hours: Horas máximas de vida de los logs

    Returns:
        Logger raíz configurado
    """
    global _log_cleaner

    # Configurar logger raíz
    root_logger = logging.getLogger("home_alexa")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Limpiar handlers existentes
    root_logger.handlers.clear()

    # Handler de consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Handler de archivo si se especifica directorio
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log general con rotación
        file_handler = RotatingFileHandler(
            log_dir / "home_alexa.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Log de errores críticos (sin auto-limpieza)
        critical_handler = RotatingFileHandler(
            log_dir / "critical.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        critical_handler.setLevel(logging.ERROR)
        critical_handler.setFormatter(file_formatter)
        root_logger.addHandler(critical_handler)

        # Iniciar limpieza automática
        if auto_cleanup and _log_cleaner is None:
            _log_cleaner = LogCleaner(log_dir, max_age_hours)
            _log_cleaner.start()

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.

    Args:
        name: Nombre del módulo (típicamente __name__)

    Returns:
        Logger configurado
    """
    if name in _loggers:
        return _loggers[name]

    # Crear logger hijo del logger raíz
    if name.startswith("home_alexa"):
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(f"home_alexa.{name}")

    _loggers[name] = logger
    return logger


def shutdown_logging():
    """Apaga el sistema de logging correctamente."""
    global _log_cleaner

    if _log_cleaner:
        _log_cleaner.stop()
        _log_cleaner = None

    logging.shutdown()
