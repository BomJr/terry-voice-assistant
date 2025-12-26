"""
Triggers Action - Terry v6.1
Manage conditional triggers (IFTTT-style)
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult
from utils.logger import get_logger

logger = get_logger(__name__)


class TriggersAction(ActionBase):
    """Triggers action for managing conditional triggers."""

    def __init__(self):
        super().__init__(
            name="triggers",
            description="Gestionar triggers condicionales (IFTTT-style)",
            description_en="Manage conditional triggers (IFTTT-style)"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute triggers action.

        Args:
            params: Action parameters
                - action: 'add', 'remove', 'list', 'enable', 'disable'
                - name: Trigger name (for add)
                - condition_type: Type of condition (for add)
                - condition_params: Condition parameters (for add)
                - action_command: Command to execute (for add)
                - trigger_id: Trigger ID (for remove/enable/disable)

        Returns:
            ActionResult with operation result
        """
        try:
            from triggers.conditional_engine import get_conditional_engine
            triggers_engine = get_conditional_engine()

            action = params.get('action', 'list')

            if action == 'add':
                # Add new conditional trigger
                name = params.get('name')
                condition_type = params.get('condition_type', 'app_open')
                condition_params = params.get('condition_params', {})
                action_command = params.get('action_command')
                description = params.get('description')

                if not all([name, action_command]):
                    return ActionResult(
                        success=False,
                        message="Necesito nombre y comando para crear un trigger"
                    )

                trigger_id = await triggers_engine.add_trigger(
                    name=name,
                    condition_type=condition_type,
                    condition_params=condition_params,
                    action_command=action_command,
                    description=description
                )

                if trigger_id:
                    return ActionResult(
                        success=True,
                        message=f"Trigger '{name}' creado",
                        data={'trigger_id': trigger_id}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude crear el trigger. Límite alcanzado?"
                    )

            elif action == 'remove':
                # Remove trigger
                trigger_id = params.get('trigger_id')

                if not trigger_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID del trigger a eliminar"
                    )

                success = await triggers_engine.remove_trigger(trigger_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Trigger eliminado"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré ese trigger"
                    )

            elif action == 'list':
                # List all triggers
                triggers = triggers_engine.list_triggers(include_disabled=True)

                if triggers:
                    # Format trigger list
                    lines = []
                    for trigger in triggers[:5]:  # Show first 5
                        status = "✅" if trigger['enabled'] else "⏸️"
                        condition = trigger['condition_type']
                        lines.append(
                            f"{status} {trigger['name']}: {condition}"
                        )

                    message = f"Tienes {len(triggers)} triggers:\n" + "\n".join(lines)

                    return ActionResult(
                        success=True,
                        message=message,
                        data={'triggers': triggers, 'count': len(triggers)}
                    )
                else:
                    return ActionResult(
                        success=True,
                        message="No tienes triggers configurados"
                    )

            elif action == 'enable':
                # Enable trigger
                trigger_id = params.get('trigger_id')

                if not trigger_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID del trigger a activar"
                    )

                success = await triggers_engine.enable_trigger(trigger_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Trigger activado"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré ese trigger"
                    )

            elif action == 'disable':
                # Disable trigger
                trigger_id = params.get('trigger_id')

                if not trigger_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el ID del trigger a desactivar"
                    )

                success = await triggers_engine.disable_trigger(trigger_id)

                if success:
                    return ActionResult(
                        success=True,
                        message="Trigger desactivado"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré ese trigger"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción de triggers no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="Triggers no está disponible. Revisa la configuración"
            )
        except Exception as e:
            logger.error(f"Error in triggers: {e}")
            return ActionResult(
                success=False,
                message=f"Error en triggers: {str(e)}"
            )
