"""
Conditional Engine - Terry v6.1
IFTTT-style conditional triggers for automation
"""
import json
import asyncio
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import subprocess
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class ConditionalTrigger:
    """Represents a conditional trigger (IF this THEN that)."""

    def __init__(self, trigger_id: str, name: str,
                 condition_type: str, condition_params: Dict[str, Any],
                 action_command: str, enabled: bool = True,
                 description: Optional[str] = None):
        """
        Initialize conditional trigger.

        Args:
            trigger_id: Unique identifier
            name: Trigger name
            condition_type: Type of condition ('app_open', 'app_close', 'time', 'pattern')
            condition_params: Parameters for condition
            action_command: Command to execute when triggered
            enabled: Whether trigger is active
            description: Optional description
        """
        self.trigger_id = trigger_id
        self.name = name
        self.condition_type = condition_type
        self.condition_params = condition_params
        self.action_command = action_command
        self.enabled = enabled
        self.description = description
        self.created_at = datetime.now()
        self.last_triggered = None
        self.trigger_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'trigger_id': self.trigger_id,
            'name': self.name,
            'condition_type': self.condition_type,
            'condition_params': self.condition_params,
            'action_command': self.action_command,
            'enabled': self.enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConditionalTrigger':
        """Create from dictionary."""
        trigger = cls(
            trigger_id=data['trigger_id'],
            name=data['name'],
            condition_type=data['condition_type'],
            condition_params=data['condition_params'],
            action_command=data['action_command'],
            enabled=data.get('enabled', True),
            description=data.get('description')
        )

        if data.get('created_at'):
            trigger.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_triggered'):
            trigger.last_triggered = datetime.fromisoformat(data['last_triggered'])
        trigger.trigger_count = data.get('trigger_count', 0)

        return trigger


class ConditionalEngine:
    """Manages conditional triggers (IFTTT-style automation)."""

    def __init__(self, max_triggers: int = 50):
        """
        Initialize Conditional Engine.

        Args:
            max_triggers: Maximum number of triggers
        """
        self.max_triggers = max_triggers
        self.triggers: Dict[str, ConditionalTrigger] = {}
        self.command_executor = None  # Set externally
        self.is_running = False

        # Active app tracking
        self.current_app = None
        self.previous_app = None

        # Storage
        self.triggers_file = Path.home() / ".terry" / "triggers" / "triggers.json"
        self.triggers_file.parent.mkdir(parents=True, exist_ok=True)

        self._load_triggers()
        logger.info("Conditional Engine initialized")

    def set_command_executor(self, executor: Callable):
        """
        Set command executor function.

        Args:
            executor: Async function that executes commands
        """
        self.command_executor = executor
        logger.debug("Command executor set for triggers")

    async def start(self):
        """Start the conditional engine monitoring."""
        if not self.is_running:
            self.is_running = True
            logger.info("Conditional Engine started")

            # Start monitoring tasks
            asyncio.create_task(self._monitor_active_app())

    async def stop(self):
        """Stop the conditional engine."""
        self.is_running = False
        logger.info("Conditional Engine stopped")

    async def add_trigger(self, name: str, condition_type: str,
                         condition_params: Dict[str, Any], action_command: str,
                         description: Optional[str] = None) -> Optional[str]:
        """
        Add a conditional trigger.

        Args:
            name: Trigger name
            condition_type: Type of condition
            condition_params: Condition parameters
            action_command: Command to execute
            description: Optional description

        Returns:
            Trigger ID if created, None if failed
        """
        if len(self.triggers) >= self.max_triggers:
            logger.warning(f"Max triggers reached: {self.max_triggers}")
            return None

        # Generate unique ID
        trigger_id = f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create trigger
        trigger = ConditionalTrigger(
            trigger_id=trigger_id,
            name=name,
            condition_type=condition_type,
            condition_params=condition_params,
            action_command=action_command,
            enabled=True,
            description=description
        )

        # Add to registry
        self.triggers[trigger_id] = trigger

        # Save to disk
        self._save_triggers()

        logger.info(f"Trigger added: {name} ({condition_type})")
        return trigger_id

    async def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger."""
        if trigger_id not in self.triggers:
            return False

        del self.triggers[trigger_id]
        self._save_triggers()

        logger.info(f"Trigger removed: {trigger_id}")
        return True

    async def enable_trigger(self, trigger_id: str) -> bool:
        """Enable a trigger."""
        if trigger_id not in self.triggers:
            return False

        self.triggers[trigger_id].enabled = True
        self._save_triggers()

        logger.info(f"Trigger enabled: {trigger_id}")
        return True

    async def disable_trigger(self, trigger_id: str) -> bool:
        """Disable a trigger."""
        if trigger_id not in self.triggers:
            return False

        self.triggers[trigger_id].enabled = False
        self._save_triggers()

        logger.info(f"Trigger disabled: {trigger_id}")
        return True

    def list_triggers(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """List all triggers."""
        triggers = []
        for trigger in self.triggers.values():
            if trigger.enabled or include_disabled:
                triggers.append(trigger.to_dict())

        return sorted(triggers, key=lambda x: x['name'])

    async def _monitor_active_app(self):
        """Monitor active application changes."""
        while self.is_running:
            try:
                # Get current active app using AppleScript
                result = subprocess.run(
                    ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    active_app = result.stdout.strip()

                    if active_app != self.current_app:
                        # App changed
                        self.previous_app = self.current_app
                        self.current_app = active_app

                        logger.debug(f"Active app changed: {self.previous_app} → {self.current_app}")

                        # Check app_open triggers
                        await self._check_app_triggers('app_open', active_app)

                        # Check app_close triggers for previous app
                        if self.previous_app:
                            await self._check_app_triggers('app_close', self.previous_app)

            except Exception as e:
                logger.debug(f"Error monitoring app: {e}")

            # Check every 2 seconds
            await asyncio.sleep(2)

    async def _check_app_triggers(self, trigger_type: str, app_name: str):
        """
        Check and execute app-related triggers.

        Args:
            trigger_type: 'app_open' or 'app_close'
            app_name: Name of the application
        """
        for trigger in self.triggers.values():
            if not trigger.enabled:
                continue

            if trigger.condition_type == trigger_type:
                target_app = trigger.condition_params.get('app_name', '').lower()

                # Match app name (case-insensitive, partial match)
                if target_app in app_name.lower() or app_name.lower() in target_app:
                    await self._execute_trigger(trigger)

    async def _execute_trigger(self, trigger: ConditionalTrigger):
        """
        Execute a trigger.

        Args:
            trigger: Trigger to execute
        """
        try:
            logger.info(f"Executing trigger: {trigger.name}")

            # Update stats
            trigger.last_triggered = datetime.now()
            trigger.trigger_count += 1
            self._save_triggers()

            # Execute command
            if self.command_executor:
                await self.command_executor(trigger.action_command)
            else:
                logger.warning("No command executor set, cannot run trigger")

        except Exception as e:
            logger.error(f"Error executing trigger {trigger.name}: {e}")

    def _save_triggers(self):
        """Save triggers to disk."""
        try:
            data = {
                trigger_id: trigger.to_dict()
                for trigger_id, trigger in self.triggers.items()
            }
            self.triggers_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving triggers: {e}")

    def _load_triggers(self):
        """Load triggers from disk."""
        if self.triggers_file.exists():
            try:
                data = json.loads(self.triggers_file.read_text())
                self.triggers = {
                    trigger_id: ConditionalTrigger.from_dict(trigger_data)
                    for trigger_id, trigger_data in data.items()
                }
                logger.info(f"Loaded {len(self.triggers)} conditional triggers")
            except Exception as e:
                logger.error(f"Error loading triggers: {e}")


# Singleton instance
_conditional_engine: Optional[ConditionalEngine] = None


def get_conditional_engine() -> ConditionalEngine:
    """
    Get the singleton ConditionalEngine instance.

    Returns:
        ConditionalEngine instance
    """
    global _conditional_engine

    if _conditional_engine is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("triggers", {})

            max_triggers = config.get("max_triggers", 50)
            _conditional_engine = ConditionalEngine(max_triggers=max_triggers)

        except Exception as e:
            logger.warning(f"Could not load triggers settings: {e}")
            _conditional_engine = ConditionalEngine()

    return _conditional_engine
