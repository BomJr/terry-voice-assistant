"""
Home-Alexa - Timer and Alarm Manager
Acciones para gestionar temporizadores, alarmas y recordatorios
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from actions.action_base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from utils.applescript_runner import run_applescript_sync, AppleScripts
from utils.logger import get_logger

logger = get_logger(__name__)


class TimerSetAction(ActionBase):
    """Crea un temporizador."""

    metadata = ActionMetadata(
        name="timer_set",
        description="Crea un temporizador",
        description_en="Creates a timer",
        category=ActionCategory.UTILITIES,
        risk_level=RiskLevel.SAFE,
        keywords_es=["temporizador", "timer", "cuenta", "regresiva", "minutos"],
        keywords_en=["timer", "countdown", "minutes"],
        required_params=["minutes"]
    )

    # Almacenamiento de timers activos (en memoria)
    _active_timers: Dict[str, asyncio.Task] = {}

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        minutes = params.get("minutes", 5)
        label = params.get("label", "Temporizador")

        try:
            minutes = float(minutes)
            if minutes <= 0:
                return ActionResult(
                    success=False,
                    message="Los minutos deben ser mayores a 0",
                    error="INVALID_MINUTES"
                )
        except (ValueError, TypeError):
            return ActionResult(
                success=False,
                message="Valor de minutos inválido",
                error="INVALID_MINUTES"
            )

        # Crear ID único para el timer
        timer_id = f"timer_{datetime.now().timestamp()}"

        # Crear tarea asíncrona para el timer
        async def timer_callback():
            await asyncio.sleep(minutes * 60)
            # Notificar cuando termine
            script = AppleScripts.display_notification(
                label,
                f"¡Temporizador de {minutes} minutos completado!"
            )
            run_applescript_sync(script)

            # También hacer un sonido
            run_applescript_sync('beep 3')

            # Limpiar del registro
            if timer_id in self._active_timers:
                del self._active_timers[timer_id]

        # Iniciar el timer
        task = asyncio.create_task(timer_callback())
        self._active_timers[timer_id] = task

        # Calcular hora de finalización
        end_time = datetime.now() + timedelta(minutes=minutes)

        return ActionResult(
            success=True,
            message=f"Temporizador de {minutes} minutos iniciado",
            data={
                "timer_id": timer_id,
                "minutes": minutes,
                "label": label,
                "ends_at": end_time.strftime("%H:%M:%S")
            }
        )

    @classmethod
    def cancel_timer(cls, timer_id: str) -> bool:
        """Cancela un timer activo."""
        if timer_id in cls._active_timers:
            cls._active_timers[timer_id].cancel()
            del cls._active_timers[timer_id]
            return True
        return False


class AlarmSetAction(ActionBase):
    """Crea una alarma."""

    metadata = ActionMetadata(
        name="alarm_set",
        description="Crea una alarma",
        description_en="Creates an alarm",
        category=ActionCategory.UTILITIES,
        risk_level=RiskLevel.SAFE,
        keywords_es=["alarma", "despertador", "despertar"],
        keywords_en=["alarm", "wake", "alert"],
        required_params=["time"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        time_str = params.get("time", "")
        label = params.get("label", "Alarma")

        if not time_str:
            return ActionResult(
                success=False,
                message="No se especificó la hora",
                error="MISSING_TIME"
            )

        # Parsear hora (formato HH:MM)
        try:
            hour, minute = map(int, time_str.split(":"))
            alarm_time = datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            # Si la hora ya pasó hoy, programar para mañana
            if alarm_time <= datetime.now():
                alarm_time += timedelta(days=1)

        except (ValueError, AttributeError):
            return ActionResult(
                success=False,
                message=f"Formato de hora inválido: {time_str}. Usar HH:MM",
                error="INVALID_TIME_FORMAT"
            )

        # Calcular segundos hasta la alarma
        seconds_until = (alarm_time - datetime.now()).total_seconds()

        # Crear tarea asíncrona para la alarma
        async def alarm_callback():
            await asyncio.sleep(seconds_until)
            # Notificar
            script = AppleScripts.display_notification(label, "¡Es hora!")
            run_applescript_sync(script)
            # Sonido de alarma
            run_applescript_sync('beep 5')

        asyncio.create_task(alarm_callback())

        return ActionResult(
            success=True,
            message=f"Alarma programada para las {time_str}",
            data={
                "time": time_str,
                "label": label,
                "alarm_datetime": alarm_time.isoformat()
            }
        )


class ReminderSetAction(ActionBase):
    """Crea un recordatorio."""

    metadata = ActionMetadata(
        name="reminder_set",
        description="Crea un recordatorio",
        description_en="Creates a reminder",
        category=ActionCategory.UTILITIES,
        risk_level=RiskLevel.SAFE,
        keywords_es=["recordatorio", "recordar", "reminder", "nota"],
        keywords_en=["reminder", "remind", "note"],
        required_params=["text"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        text = params.get("text", "")
        time_str = params.get("time")  # Opcional
        minutes = params.get("minutes")  # Alternativa

        if not text:
            return ActionResult(
                success=False,
                message="No se especificó el texto del recordatorio",
                error="MISSING_TEXT"
            )

        trigger_time = None

        # Determinar cuándo disparar el recordatorio
        if time_str:
            try:
                hour, minute = map(int, time_str.split(":"))
                trigger_time = datetime.now().replace(
                    hour=hour, minute=minute, second=0
                )
                if trigger_time <= datetime.now():
                    trigger_time += timedelta(days=1)
            except (ValueError, AttributeError):
                pass

        elif minutes:
            try:
                trigger_time = datetime.now() + timedelta(minutes=float(minutes))
            except (ValueError, TypeError):
                pass

        if trigger_time:
            seconds_until = (trigger_time - datetime.now()).total_seconds()

            async def reminder_callback():
                await asyncio.sleep(seconds_until)
                script = AppleScripts.display_notification(
                    "Recordatorio",
                    text
                )
                run_applescript_sync(script)
                run_applescript_sync('beep 2')

            asyncio.create_task(reminder_callback())

            return ActionResult(
                success=True,
                message=f"Recordatorio programado: {text}",
                data={
                    "text": text,
                    "trigger_at": trigger_time.isoformat()
                }
            )
        else:
            # Recordatorio inmediato (mostrar ahora)
            script = AppleScripts.display_notification("Recordatorio", text)
            run_applescript_sync(script)

            return ActionResult(
                success=True,
                message=f"Recordatorio: {text}",
                data={"text": text}
            )
