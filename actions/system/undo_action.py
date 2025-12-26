"""
Undo Action - Terry v6.1
Undo the last executed action
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult, ActionCategory
from undo.action_history import get_action_history
from actions.action_registry import ActionRegistry
from utils.logger import get_logger

logger = get_logger(__name__)


class UndoAction(ActionBase):
    """Action for undoing the last executed action."""

    def __init__(self):
        """Initialize Undo Action."""
        super().__init__(
            name="undo",
            description="Deshacer la última acción ejecutada",
            description_en="Undo the last executed action",
            category=ActionCategory.SYSTEM
        )

        # Set metadata
        self.metadata.required_params = []
        self.metadata.keywords_es = [
            "deshacer", "deshaz", "undo", "volver atrás",
            "revertir", "cancelar último", "vuelve"
        ]
        self.metadata.keywords_en = [
            "undo", "revert", "go back", "cancel last"
        ]

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute the undo action.

        Args:
            params: Action parameters (none required)

        Returns:
            ActionResult with success status and message
        """
        history = get_action_history()

        # Check if there's anything to undo
        if not history.can_undo():
            last_action = history.get_last_action()
            if last_action:
                return ActionResult(
                    success=False,
                    message=f"La última acción ({last_action.action_type}) no se puede deshacer"
                )
            else:
                return ActionResult(
                    success=False,
                    message="No hay acciones para deshacer"
                )

        # Get last action details
        last = history.get_last_action()
        undo_params = history.get_undo_params()

        if not last or not undo_params:
            return ActionResult(
                success=False,
                message="No se puede deshacer la última acción"
            )

        logger.info(f"Undoing action: {last.action_type} with params {undo_params}")

        try:
            # Get the action from registry
            registry = ActionRegistry()
            action_type = last.action_type

            # Handle special undo cases
            if action_type == "open_app":
                # Special case: undo open_app by quitting
                # This would require a quit_app action (not implemented yet)
                # For now, just tell the user
                app_name = last.params.get('app_name', 'aplicación')
                history.pop_last()
                return ActionResult(
                    success=True,
                    message=f"Para deshacer, cierra {app_name} manualmente",
                    data={'undone_action': action_type, 'manual': True}
                )

            elif action_type == "browser_open_url" or action_type == "browser_new_tab":
                # Special case: undo browser actions by closing tab
                action = registry.get("browser_close_tab")
                if action:
                    result = await action.execute({})
                    if result.success:
                        history.pop_last()
                        return ActionResult(
                            success=True,
                            message=f"Deshecho: {action_type}",
                            data={'undone_action': action_type}
                        )

            else:
                # Normal case: execute the reverse action
                action = registry.get(action_type)

                if action:
                    # Execute with undo parameters
                    result = await action.execute(undo_params)

                    if result.success:
                        # Remove from history
                        history.pop_last()

                        # Build success message
                        action_names = {
                            'volume_set': 'volumen',
                            'volume_up': 'subir volumen',
                            'volume_down': 'bajar volumen',
                            'volume_mute': 'silenciar',
                            'media_play': 'reproducir',
                            'media_pause': 'pausar',
                            'silent_mode': 'modo silencioso',
                            'voice_notes': 'nota'
                        }

                        action_name = action_names.get(action_type, action_type)

                        return ActionResult(
                            success=True,
                            message=f"Deshecho: {action_name}",
                            data={'undone_action': action_type}
                        )
                    else:
                        return ActionResult(
                            success=False,
                            message=f"Error deshaciendo: {result.message}"
                        )

            # If we get here, action not found
            return ActionResult(
                success=False,
                message=f"No se puede deshacer {action_type}"
            )

        except Exception as e:
            logger.error(f"Error in undo action: {e}", exc_info=True)
            return ActionResult(
                success=False,
                message=f"Error deshaciendo: {str(e)}"
            )
