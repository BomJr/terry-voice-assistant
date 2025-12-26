"""
Scheduler Action - Terry v6.1
Manage scheduled routines
"""
from typing import Any, Dict
from terry.core.actions.base import ActionBase, ActionResult
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class SchedulerAction(ActionBase):
    """Scheduler action for managing scheduled routines."""

    def __init__(self):
        super().__init__(
            name="scheduler",
            description="Gestionar rutinas programadas",
            description_en="Manage scheduled routines"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute scheduler action.

        Args:
            params: Action parameters
                - action: 'add', 'remove', 'list', 'enable', 'disable'
                - name: Routine name (for add)
                - command: Command to schedule (for add)
                - schedule: Schedule expression (for add)
                - routine_id: Routine ID (for remove/enable/disable)

        Returns:
            ActionResult with operation result
        """
        try:
            from terry.features.automation.cron_manager import get_cron_manager
            scheduler = get_cron_manager()

            action = params.get('action', 'list')

            if action == 'add':
                # Add new scheduled routine
                name = params.get('name')
                command = params.get('command')
                schedule = params.get('schedule')
                description = params.get('description')

                if not all([name, command, schedule]):
                    return ActionResult(
                        success=False,
                        message="Necesito nombre, comando y horario para crear una rutina"
                    )

                routine_id = await scheduler.add_routine(
                    name=name,
                    command=command,
                    schedule=schedule,
                    description=description
                )

                if routine_id:
                    return ActionResult(
                        success=True,
                        message=f"Rutina '{name}' programada: {schedule}",
                        data={'routine_id': routine_id}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude crear la rutina. Límite alcanzado?"
                    )

            elif action == 'remove':
                # Remove routine
                routine_id = params.get('routine_id')

                if not routine_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID de la rutina a eliminar"
                    )

                success = await scheduler.remove_routine(routine_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Rutina eliminada"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré esa rutina"
                    )

            elif action == 'list':
                # List all routines
                routines = scheduler.list_routines(include_disabled=True)

                if routines:
                    # Format routine list
                    lines = []
                    for routine in routines[:5]:  # Show first 5
                        status = "✅" if routine['enabled'] else "⏸️"
                        lines.append(
                            f"{status} {routine['name']}: {routine['schedule']}"
                        )

                    message = f"Tienes {len(routines)} rutinas programadas:\n" + "\n".join(lines)

                    return ActionResult(
                        success=True,
                        message=message,
                        data={'routines': routines, 'count': len(routines)}
                    )
                else:
                    return ActionResult(
                        success=True,
                        message="No tienes rutinas programadas"
                    )

            elif action == 'enable':
                # Enable routine
                routine_id = params.get('routine_id')

                if not routine_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID de la rutina a activar"
                    )

                success = await scheduler.enable_routine(routine_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Rutina activada"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré esa rutina"
                    )

            elif action == 'disable':
                # Disable routine
                routine_id = params.get('routine_id')

                if not routine_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID de la rutina a desactivar"
                    )

                success = await scheduler.disable_routine(routine_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Rutina desactivada"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré esa rutina"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción de scheduler no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="Scheduler no está disponible. Revisa la configuración"
            )
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            return ActionResult(
                success=False,
                message=f"Error en scheduler: {str(e)}"
            )
