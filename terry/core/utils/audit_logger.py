"""
Home-Alexa - Audit Logger
Registra todos los comandos ejecutados para auditoría
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class AuditLogger:
    """Registra comandos ejecutados para auditoría."""

    def __init__(self, audit_file: str = "logs/audit.log"):
        """
        Inicializa el logger de auditoría.

        Args:
            audit_file: Ruta al archivo de auditoría
        """
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(exist_ok=True)

        # Crear archivo si no existe
        if not self.audit_file.exists():
            self.audit_file.touch()

    def log_command(
        self,
        user_input: str,
        intent: str,
        actions: list,
        success: bool,
        response: str,
        execution_time: float,
        cached: bool = False,
        error: Optional[str] = None
    ):
        """
        Registra un comando ejecutado.

        Args:
            user_input: Comando del usuario
            intent: Intención detectada
            actions: Lista de acciones ejecutadas
            success: Si el comando tuvo éxito
            response: Respuesta generada
            execution_time: Tiempo de ejecución en segundos
            cached: Si la respuesta vino del caché
            error: Mensaje de error si hubo alguno
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "unix_time": time.time(),
            "user_input": user_input,
            "intent": intent,
            "actions": [
                {
                    "type": action.get("type", "unknown"),
                    "params": action.get("params", {})
                }
                for action in actions
            ],
            "success": success,
            "response": response,
            "execution_time_ms": round(execution_time * 1000, 2),
            "cached": cached,
            "error": error
        }

        try:
            # Escribir como JSON Lines (una línea por entrada)
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False)
                f.write('\n')

            logger.debug(f"Comando auditado: {intent} (success={success})")

        except Exception as e:
            logger.error(f"Error escribiendo auditoría: {e}")

    def get_recent_commands(self, limit: int = 10) -> list:
        """
        Obtiene los comandos recientes del log de auditoría.

        Args:
            limit: Número máximo de comandos

        Returns:
            Lista de comandos recientes
        """
        if not self.audit_file.exists():
            return []

        try:
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Leer últimas N líneas
            recent_lines = lines[-limit:] if len(lines) >= limit else lines

            # Parsear JSON
            commands = []
            for line in reversed(recent_lines):  # Más reciente primero
                try:
                    commands.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

            return commands

        except Exception as e:
            logger.error(f"Error leyendo auditoría: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del log de auditoría.

        Returns:
            Diccionario con estadísticas
        """
        if not self.audit_file.exists():
            return {
                "total_commands": 0,
                "successful": 0,
                "failed": 0,
                "cached": 0
            }

        try:
            with open(self.audit_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total = 0
            successful = 0
            failed = 0
            cached = 0
            total_time = 0.0
            intent_counts = {}

            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    total += 1

                    if entry.get("success"):
                        successful += 1
                    else:
                        failed += 1

                    if entry.get("cached"):
                        cached += 1

                    total_time += entry.get("execution_time_ms", 0)

                    intent = entry.get("intent", "unknown")
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1

                except json.JSONDecodeError:
                    continue

            # Calcular promedios
            avg_time = total_time / total if total > 0 else 0
            success_rate = (successful / total * 100) if total > 0 else 0
            cache_rate = (cached / total * 100) if total > 0 else 0

            # Top intents
            top_intents = sorted(
                intent_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                "total_commands": total,
                "successful": successful,
                "failed": failed,
                "cached": cached,
                "success_rate": f"{success_rate:.1f}%",
                "cache_rate": f"{cache_rate:.1f}%",
                "avg_execution_time_ms": f"{avg_time:.2f}",
                "top_intents": top_intents
            }

        except Exception as e:
            logger.error(f"Error obteniendo stats de auditoría: {e}")
            return {}

    def print_stats(self):
        """Imprime estadísticas del log de auditoría."""
        stats = self.get_stats()

        if stats.get("total_commands", 0) == 0:
            print("\n📋 AUDITORÍA: No hay comandos registrados")
            return

        print("\n📋 ESTADÍSTICAS DE AUDITORÍA")
        print("=" * 60)
        print(f"  Total comandos: {stats['total_commands']}")
        print(f"  Exitosos: {stats['successful']} ({stats['success_rate']})")
        print(f"  Fallidos: {stats['failed']}")
        print(f"  Desde caché: {stats['cached']} ({stats['cache_rate']})")
        print(f"  Tiempo promedio: {stats['avg_execution_time_ms']} ms")

        if stats.get('top_intents'):
            print("\n  Top Intenciones:")
            for intent, count in stats['top_intents']:
                print(f"    • {intent}: {count} veces")

        print("=" * 60)

    def print_recent(self, limit: int = 10):
        """Imprime comandos recientes."""
        commands = self.get_recent_commands(limit)

        if not commands:
            print("\n📋 No hay comandos recientes")
            return

        print(f"\n📋 ÚLTIMOS {len(commands)} COMANDOS")
        print("=" * 60)

        for idx, cmd in enumerate(commands, 1):
            timestamp = cmd.get("timestamp", "")
            user_input = cmd.get("user_input", "")
            intent = cmd.get("intent", "")
            success = "✅" if cmd.get("success") else "❌"
            cached = "⚡" if cmd.get("cached") else ""
            exec_time = cmd.get("execution_time_ms", 0)

            print(f"\n{idx}. [{timestamp}]")
            print(f"   Usuario: {user_input}")
            print(f"   Intent: {intent} {success} {cached}")
            print(f"   Tiempo: {exec_time} ms")

        print("=" * 60)

    def clear_old_entries(self, days: int = 30):
        """
        Elimina entradas más antiguas que N días.

        Args:
            days: Días de antigüedad máxima
        """
        if not self.audit_file.exists():
            return

        try:
            cutoff_time = time.time() - (days * 86400)
            kept_lines = []

            with open(self.audit_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("unix_time", 0) >= cutoff_time:
                            kept_lines.append(line)
                    except json.JSONDecodeError:
                        continue

            # Reescribir archivo
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                f.writelines(kept_lines)

            removed = len(kept_lines)
            logger.info(f"Limpieza de auditoría: mantenidas {removed} entradas")

        except Exception as e:
            logger.error(f"Error limpiando auditoría: {e}")


# Instancia global
_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Obtiene la instancia global del audit logger."""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance
