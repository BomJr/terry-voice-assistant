"""
Action History Manager - Terry v6.1
Track and undo actions with intelligent reversal
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ActionRecord:
    """Record of an executed action."""
    action_type: str
    params: Dict[str, Any]
    timestamp: str  # ISO format
    result: Dict[str, Any]
    reversible: bool = False
    undo_params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionRecord':
        """Create from dictionary."""
        return cls(**data)


class ActionHistory:
    """Manages action history for undo functionality."""

    def __init__(self, max_history: int = 10):
        """
        Initialize Action History.

        Args:
            max_history: Maximum number of actions to keep in history
        """
        self.max_history = max_history
        self.history: List[ActionRecord] = []
        self.history_file = Path.home() / ".terry" / "action_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_history()

        logger.info(f"Action History initialized (max: {max_history})")

    def record(self, action_type: str, params: Dict[str, Any],
               result: Dict[str, Any], reversible: bool = False,
               undo_params: Optional[Dict[str, Any]] = None):
        """
        Record an executed action.

        Args:
            action_type: Type of action executed
            params: Parameters used for the action
            result: Result of the action execution
            reversible: Whether this action can be undone
            undo_params: Parameters to use for undoing the action
        """
        record = ActionRecord(
            action_type=action_type,
            params=params,
            timestamp=datetime.now().isoformat(),
            result=result,
            reversible=reversible,
            undo_params=undo_params
        )

        self.history.append(record)

        # Trim history if exceeds max
        if len(self.history) > self.max_history:
            self.history.pop(0)

        self._save_history()
        logger.debug(f"Action recorded: {action_type} (reversible={reversible})")

    def get_last_action(self) -> Optional[ActionRecord]:
        """
        Get the last executed action.

        Returns:
            Last ActionRecord or None if history is empty
        """
        return self.history[-1] if self.history else None

    def can_undo(self) -> bool:
        """
        Check if the last action can be undone.

        Returns:
            True if last action is reversible
        """
        last = self.get_last_action()
        return last is not None and last.reversible

    def get_undo_params(self) -> Optional[Dict[str, Any]]:
        """
        Get parameters for undoing the last action.

        Returns:
            Undo parameters or None
        """
        if self.can_undo():
            return self.history[-1].undo_params
        return None

    def get_last_action_type(self) -> Optional[str]:
        """Get the type of the last action."""
        last = self.get_last_action()
        return last.action_type if last else None

    def pop_last(self):
        """Remove last action from history after successful undo."""
        if self.history:
            removed = self.history.pop()
            self._save_history()
            logger.info(f"Action removed from history: {removed.action_type}")

    def get_history(self, limit: Optional[int] = None) -> List[ActionRecord]:
        """
        Get action history.

        Args:
            limit: Maximum number of records to return (most recent first)

        Returns:
            List of ActionRecords
        """
        if limit:
            return list(reversed(self.history[-limit:]))
        return list(reversed(self.history))

    def clear_history(self):
        """Clear all action history."""
        self.history.clear()
        self._save_history()
        logger.info("Action history cleared")

    def _save_history(self):
        """Save history to disk."""
        try:
            data = [record.to_dict() for record in self.history]
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving action history: {e}")

    def _load_history(self):
        """Load history from disk."""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text())
                self.history = [ActionRecord.from_dict(r) for r in data]
                logger.debug(f"Loaded {len(self.history)} actions from history")
            except Exception as e:
                logger.error(f"Error loading action history: {e}")
                self.history = []

    def get_reversible_actions_count(self) -> int:
        """Get count of reversible actions in history."""
        return sum(1 for record in self.history if record.reversible)


# Singleton instance
_action_history: Optional[ActionHistory] = None


def get_action_history() -> ActionHistory:
    """
    Get the singleton ActionHistory instance.

    Returns:
        ActionHistory instance
    """
    global _action_history

    if _action_history is None:
        try:
            from config.settings import settings
            max_history = settings.get("undo_system", {}).get("max_history", 10)
            _action_history = ActionHistory(max_history=max_history)
        except Exception as e:
            logger.warning(f"Could not load settings for undo system: {e}")
            _action_history = ActionHistory()

    return _action_history


def determine_undo_params(action_type: str, params: Dict[str, Any],
                          result_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Determine if an action is reversible and get undo parameters.

    Args:
        action_type: Type of action
        params: Parameters used for the action
        result_data: Result data from the action

    Returns:
        Tuple of (reversible: bool, undo_params: Dict or None)
    """
    # Volume actions - save previous volume
    if action_type == "volume_set":
        previous_volume = result_data.get('previous_volume')
        if previous_volume is not None:
            return True, {'level': previous_volume}

    elif action_type in ["volume_up", "volume_down"]:
        previous_volume = result_data.get('previous_volume')
        if previous_volume is not None:
            return True, {'level': previous_volume}

    # Mute/unmute actions
    elif action_type == "volume_mute":
        was_muted = result_data.get('was_muted', False)
        if not was_muted:
            # If it wasn't muted before, undo should unmute
            return True, {'unmute': True}

    # Media actions - toggle between play/pause
    elif action_type == "media_play":
        return True, {'action': 'pause'}

    elif action_type == "media_pause":
        return True, {'action': 'play'}

    # Silent mode - toggle
    elif action_type == "silent_mode":
        current_state = result_data.get('silent', False)
        # Undo by toggling back
        opposite_mode = 'off' if current_state else 'on'
        return True, {'mode': opposite_mode}

    # Browser actions - close what was opened
    elif action_type == "browser_open_url":
        # Can undo by closing the tab (browser_close_tab)
        return True, {'action': 'close_tab'}

    elif action_type == "browser_new_tab":
        return True, {'action': 'close_tab'}

    # Application actions
    elif action_type == "open_app":
        app_name = params.get('app_name')
        if app_name:
            # Can undo by quitting the app
            return True, {'app_name': app_name, 'action': 'quit'}

    # Voice notes actions
    elif action_type == "voice_notes":
        note_action = params.get('action')
        if note_action == 'add':
            note_id = result_data.get('note_id')
            if note_id:
                # Undo add by deleting
                return True, {'action': 'delete', 'note_id': note_id}

        elif note_action == 'complete':
            note_id = result_data.get('note_id')
            if note_id:
                # Undo complete by marking uncompleted
                return True, {'action': 'uncomplete', 'note_id': note_id}

        elif note_action == 'delete':
            # Cannot undo delete (data is gone)
            return False, None

    # Most actions are not reversible by default
    return False, None
