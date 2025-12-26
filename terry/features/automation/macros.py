"""
Macro Recorder - Terry v6.1
Record and replay action sequences
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class Macro:
    """Represents a recorded macro."""

    def __init__(self, macro_id: str, name: str, commands: List[str],
                 description: Optional[str] = None):
        """
        Initialize Macro.

        Args:
            macro_id: Unique identifier
            name: Macro name
            commands: List of commands to execute
            description: Optional description
        """
        self.macro_id = macro_id
        self.name = name
        self.commands = commands
        self.description = description
        self.created_at = datetime.now()
        self.last_executed = None
        self.execution_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'macro_id': self.macro_id,
            'name': self.name,
            'commands': self.commands,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_executed': self.last_executed.isoformat() if self.last_executed else None,
            'execution_count': self.execution_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Macro':
        """Create from dictionary."""
        macro = cls(
            macro_id=data['macro_id'],
            name=data['name'],
            commands=data['commands'],
            description=data.get('description')
        )

        if data.get('created_at'):
            macro.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_executed'):
            macro.last_executed = datetime.fromisoformat(data['last_executed'])
        macro.execution_count = data.get('execution_count', 0)

        return macro


class MacroRecorder:
    """Records and manages command macros."""

    def __init__(self, max_macros: int = 30, macros_directory: Optional[str] = None):
        """
        Initialize Macro Recorder.

        Args:
            max_macros: Maximum number of macros
            macros_directory: Directory to store macros
        """
        self.max_macros = max_macros
        self.macros_dir = Path(macros_directory or str(Path.home() / ".terry" / "macros"))
        self.macros_dir.mkdir(parents=True, exist_ok=True)

        self.macros: Dict[str, Macro] = {}
        self.recording = False
        self.current_recording: List[str] = []
        self.recording_name: Optional[str] = None

        self.command_executor = None  # Set externally

        self._load_macros()
        logger.info("Macro Recorder initialized")

    def set_command_executor(self, executor: Callable):
        """
        Set command executor function.

        Args:
            executor: Async function that executes commands
        """
        self.command_executor = executor
        logger.debug("Command executor set for macros")

    def start_recording(self, name: str) -> bool:
        """
        Start recording a macro.

        Args:
            name: Name for the macro

        Returns:
            True if recording started, False if already recording or name exists
        """
        if self.recording:
            logger.warning("Already recording a macro")
            return False

        # Check if name already exists
        if any(m.name.lower() == name.lower() for m in self.macros.values()):
            logger.warning(f"Macro with name '{name}' already exists")
            return False

        # Check macro limit
        if len(self.macros) >= self.max_macros:
            logger.warning(f"Max macros reached: {self.max_macros}")
            return False

        self.recording = True
        self.recording_name = name
        self.current_recording = []

        logger.info(f"Started recording macro: {name}")
        return True

    def record_command(self, command: str):
        """
        Record a command in the current macro.

        Args:
            command: Command to record
        """
        if not self.recording:
            return

        # Don't record macro-related commands
        if any(keyword in command.lower() for keyword in ['graba', 'detén', 'ejecuta', 'macro', 'record', 'stop']):
            return

        self.current_recording.append(command)
        logger.debug(f"Recorded command: {command}")

    def stop_recording(self, save: bool = True) -> Optional[str]:
        """
        Stop recording and optionally save the macro.

        Args:
            save: Whether to save the macro

        Returns:
            Macro ID if saved, None otherwise
        """
        if not self.recording:
            logger.warning("Not currently recording")
            return None

        self.recording = False

        if save and self.current_recording:
            # Generate unique ID
            macro_id = f"macro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create macro
            macro = Macro(
                macro_id=macro_id,
                name=self.recording_name,
                commands=self.current_recording.copy()
            )

            # Save
            self.macros[macro_id] = macro
            self._save_macro(macro)

            logger.info(f"Saved macro '{self.recording_name}' with {len(self.current_recording)} commands")

            # Reset recording state
            self.current_recording = []
            self.recording_name = None

            return macro_id
        else:
            logger.info("Recording cancelled or empty")
            self.current_recording = []
            self.recording_name = None
            return None

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording

    def get_recording_status(self) -> Dict[str, Any]:
        """Get current recording status."""
        return {
            'recording': self.recording,
            'name': self.recording_name,
            'commands_count': len(self.current_recording),
            'commands': self.current_recording.copy() if self.recording else []
        }

    async def execute_macro(self, macro_id: Optional[str] = None,
                           macro_name: Optional[str] = None) -> bool:
        """
        Execute a macro by ID or name.

        Args:
            macro_id: Macro ID to execute
            macro_name: Macro name to execute (if ID not provided)

        Returns:
            True if executed successfully, False otherwise
        """
        # Find macro
        macro = None

        if macro_id:
            macro = self.macros.get(macro_id)
        elif macro_name:
            for m in self.macros.values():
                if m.name.lower() == macro_name.lower():
                    macro = m
                    break

        if not macro:
            logger.warning(f"Macro not found: {macro_id or macro_name}")
            return False

        if not self.command_executor:
            logger.warning("No command executor set, cannot execute macro")
            return False

        try:
            logger.info(f"Executing macro: {macro.name} ({len(macro.commands)} commands)")

            # Update stats
            macro.last_executed = datetime.now()
            macro.execution_count += 1
            self._save_macro(macro)

            # Execute each command
            for command in macro.commands:
                logger.debug(f"Executing macro command: {command}")
                await self.command_executor(command)

                # Small delay between commands
                import asyncio
                await asyncio.sleep(0.5)

            logger.info(f"Macro '{macro.name}' executed successfully")
            return True

        except Exception as e:
            logger.error(f"Error executing macro {macro.name}: {e}")
            return False

    def list_macros(self) -> List[Dict[str, Any]]:
        """List all macros."""
        return [macro.to_dict() for macro in sorted(self.macros.values(), key=lambda x: x.name)]

    def get_macro(self, macro_id: Optional[str] = None,
                  macro_name: Optional[str] = None) -> Optional[Macro]:
        """Get macro by ID or name."""
        if macro_id:
            return self.macros.get(macro_id)

        if macro_name:
            for macro in self.macros.values():
                if macro.name.lower() == macro_name.lower():
                    return macro

        return None

    def delete_macro(self, macro_id: Optional[str] = None,
                    macro_name: Optional[str] = None) -> bool:
        """Delete a macro."""
        macro = self.get_macro(macro_id, macro_name)

        if not macro:
            return False

        # Delete file
        macro_file = self.macros_dir / f"{macro.macro_id}.json"
        if macro_file.exists():
            macro_file.unlink()

        # Remove from registry
        del self.macros[macro.macro_id]

        logger.info(f"Deleted macro: {macro.name}")
        return True

    def _save_macro(self, macro: Macro):
        """Save macro to disk."""
        try:
            macro_file = self.macros_dir / f"{macro.macro_id}.json"
            macro_file.write_text(json.dumps(macro.to_dict(), indent=2))
        except Exception as e:
            logger.error(f"Error saving macro: {e}")

    def _load_macros(self):
        """Load all macros from disk."""
        try:
            for macro_file in self.macros_dir.glob("*.json"):
                try:
                    data = json.loads(macro_file.read_text())
                    macro = Macro.from_dict(data)
                    self.macros[macro.macro_id] = macro
                except Exception as e:
                    logger.error(f"Error loading macro {macro_file}: {e}")

            logger.info(f"Loaded {len(self.macros)} macros")
        except Exception as e:
            logger.error(f"Error loading macros: {e}")


# Singleton instance
_macro_recorder: Optional[MacroRecorder] = None


def get_macro_recorder() -> MacroRecorder:
    """
    Get the singleton MacroRecorder instance.

    Returns:
        MacroRecorder instance
    """
    global _macro_recorder

    if _macro_recorder is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("macros", {})

            max_macros = config.get("max_macros", 30)
            macros_dir = config.get("macros_directory")

            _macro_recorder = MacroRecorder(
                max_macros=max_macros,
                macros_directory=macros_dir
            )

        except Exception as e:
            logger.warning(f"Could not load macros settings: {e}")
            _macro_recorder = MacroRecorder()

    return _macro_recorder
