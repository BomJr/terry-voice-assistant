"""
Cron Manager - Terry v6.1
Scheduled routines with cron-style scheduling
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from utils.logger import get_logger

logger = get_logger(__name__)


class ScheduledRoutine:
    """Represents a scheduled routine."""

    def __init__(self, routine_id: str, name: str, command: str,
                 schedule: str, enabled: bool = True,
                 description: Optional[str] = None):
        """
        Initialize scheduled routine.

        Args:
            routine_id: Unique identifier
            name: Routine name
            command: Command to execute
            schedule: Cron expression or schedule type
            enabled: Whether routine is active
            description: Optional description
        """
        self.routine_id = routine_id
        self.name = name
        self.command = command
        self.schedule = schedule
        self.enabled = enabled
        self.description = description
        self.created_at = datetime.now()
        self.last_run = None
        self.run_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'routine_id': self.routine_id,
            'name': self.name,
            'command': self.command,
            'schedule': self.schedule,
            'enabled': self.enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledRoutine':
        """Create from dictionary."""
        routine = cls(
            routine_id=data['routine_id'],
            name=data['name'],
            command=data['command'],
            schedule=data['schedule'],
            enabled=data.get('enabled', True),
            description=data.get('description')
        )

        if data.get('created_at'):
            routine.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_run'):
            routine.last_run = datetime.fromisoformat(data['last_run'])
        routine.run_count = data.get('run_count', 0)

        return routine


class CronManager:
    """Manages scheduled routines with cron-style scheduling."""

    def __init__(self, max_routines: int = 20):
        """
        Initialize Cron Manager.

        Args:
            max_routines: Maximum number of scheduled routines
        """
        self.max_routines = max_routines
        self.routines: Dict[str, ScheduledRoutine] = {}
        self.scheduler = AsyncIOScheduler()
        self.command_executor = None  # Set externally

        # Storage
        self.routines_file = Path.home() / ".terry" / "scheduler" / "routines.json"
        self.routines_file.parent.mkdir(parents=True, exist_ok=True)

        self._load_routines()
        logger.info("Cron Manager initialized")

    def set_command_executor(self, executor: Callable):
        """
        Set command executor function.

        Args:
            executor: Async function that executes commands
        """
        self.command_executor = executor
        logger.debug("Command executor set")

    async def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

            # Schedule all enabled routines
            for routine in self.routines.values():
                if routine.enabled:
                    await self._schedule_routine(routine)

    async def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    async def add_routine(self, name: str, command: str, schedule: str,
                         description: Optional[str] = None) -> Optional[str]:
        """
        Add a scheduled routine.

        Args:
            name: Routine name
            command: Command to execute
            schedule: Schedule expression (cron, interval, or time)
            description: Optional description

        Returns:
            Routine ID if created, None if failed
        """
        if len(self.routines) >= self.max_routines:
            logger.warning(f"Max routines reached: {self.max_routines}")
            return None

        # Generate unique ID
        routine_id = f"routine_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create routine
        routine = ScheduledRoutine(
            routine_id=routine_id,
            name=name,
            command=command,
            schedule=schedule,
            enabled=True,
            description=description
        )

        # Add to registry
        self.routines[routine_id] = routine

        # Schedule it
        await self._schedule_routine(routine)

        # Save to disk
        self._save_routines()

        logger.info(f"Routine added: {name} ({schedule})")
        return routine_id

    async def remove_routine(self, routine_id: str) -> bool:
        """
        Remove a scheduled routine.

        Args:
            routine_id: Routine ID to remove

        Returns:
            True if removed, False if not found
        """
        if routine_id not in self.routines:
            return False

        # Remove from scheduler
        try:
            self.scheduler.remove_job(routine_id)
        except Exception:
            pass

        # Remove from registry
        del self.routines[routine_id]

        # Save to disk
        self._save_routines()

        logger.info(f"Routine removed: {routine_id}")
        return True

    async def enable_routine(self, routine_id: str) -> bool:
        """Enable a routine."""
        if routine_id not in self.routines:
            return False

        routine = self.routines[routine_id]
        routine.enabled = True

        await self._schedule_routine(routine)
        self._save_routines()

        logger.info(f"Routine enabled: {routine_id}")
        return True

    async def disable_routine(self, routine_id: str) -> bool:
        """Disable a routine."""
        if routine_id not in self.routines:
            return False

        routine = self.routines[routine_id]
        routine.enabled = False

        # Remove from scheduler
        try:
            self.scheduler.remove_job(routine_id)
        except Exception:
            pass

        self._save_routines()

        logger.info(f"Routine disabled: {routine_id}")
        return True

    def list_routines(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        List all routines.

        Args:
            include_disabled: Include disabled routines

        Returns:
            List of routine dictionaries
        """
        routines = []
        for routine in self.routines.values():
            if routine.enabled or include_disabled:
                routines.append(routine.to_dict())

        return sorted(routines, key=lambda x: x['name'])

    def get_routine(self, routine_id: str) -> Optional[ScheduledRoutine]:
        """Get routine by ID."""
        return self.routines.get(routine_id)

    async def _schedule_routine(self, routine: ScheduledRoutine):
        """
        Schedule a routine in APScheduler.

        Args:
            routine: Routine to schedule
        """
        try:
            # Remove existing job if any
            try:
                self.scheduler.remove_job(routine.routine_id)
            except Exception:
                pass

            # Parse schedule and create trigger
            trigger = self._parse_schedule(routine.schedule)

            if trigger:
                # Add job
                self.scheduler.add_job(
                    func=self._execute_routine,
                    trigger=trigger,
                    id=routine.routine_id,
                    name=routine.name,
                    args=[routine],
                    replace_existing=True
                )

                logger.debug(f"Scheduled: {routine.name} ({routine.schedule})")
            else:
                logger.warning(f"Invalid schedule: {routine.schedule}")

        except Exception as e:
            logger.error(f"Error scheduling routine: {e}")

    def _parse_schedule(self, schedule: str):
        """
        Parse schedule string into APScheduler trigger.

        Supported formats:
        - Cron: "0 9 * * MON-FRI" (every weekday at 9 AM)
        - Time: "09:00" (daily at 9 AM)
        - Interval: "every 1 hour", "every 30 minutes"

        Args:
            schedule: Schedule string

        Returns:
            Trigger object or None
        """
        schedule_lower = schedule.lower().strip()

        # Interval format: "every X minutes/hours/days"
        if schedule_lower.startswith("every "):
            parts = schedule_lower.split()
            if len(parts) >= 3:
                try:
                    value = int(parts[1])
                    unit = parts[2].rstrip('s')  # Remove plural 's'

                    if unit == 'minute':
                        return IntervalTrigger(minutes=value)
                    elif unit == 'hour':
                        return IntervalTrigger(hours=value)
                    elif unit == 'day':
                        return IntervalTrigger(days=value)
                except ValueError:
                    pass

        # Time format: "HH:MM"
        if ':' in schedule and len(schedule.split(':')) == 2:
            try:
                hour, minute = schedule.split(':')
                return CronTrigger(hour=int(hour), minute=int(minute))
            except ValueError:
                pass

        # Cron format: "minute hour day month day_of_week"
        parts = schedule.split()
        if len(parts) == 5:
            try:
                return CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4]
                )
            except Exception:
                pass

        logger.warning(f"Could not parse schedule: {schedule}")
        return None

    async def _execute_routine(self, routine: ScheduledRoutine):
        """
        Execute a scheduled routine.

        Args:
            routine: Routine to execute
        """
        try:
            logger.info(f"Executing scheduled routine: {routine.name}")

            # Update stats
            routine.last_run = datetime.now()
            routine.run_count += 1
            self._save_routines()

            # Execute command
            if self.command_executor:
                await self.command_executor(routine.command)
            else:
                logger.warning("No command executor set, cannot run routine")

        except Exception as e:
            logger.error(f"Error executing routine {routine.name}: {e}")

    def _save_routines(self):
        """Save routines to disk."""
        try:
            data = {
                routine_id: routine.to_dict()
                for routine_id, routine in self.routines.items()
            }
            self.routines_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving routines: {e}")

    def _load_routines(self):
        """Load routines from disk."""
        if self.routines_file.exists():
            try:
                data = json.loads(self.routines_file.read_text())
                self.routines = {
                    routine_id: ScheduledRoutine.from_dict(routine_data)
                    for routine_id, routine_data in data.items()
                }
                logger.info(f"Loaded {len(self.routines)} scheduled routines")
            except Exception as e:
                logger.error(f"Error loading routines: {e}")


# Singleton instance
_cron_manager: Optional[CronManager] = None


def get_cron_manager() -> CronManager:
    """
    Get the singleton CronManager instance.

    Returns:
        CronManager instance
    """
    global _cron_manager

    if _cron_manager is None:
        try:
            from config.settings import settings
            config = settings.get("scheduler", {})

            max_routines = config.get("max_scheduled_routines", 20)
            _cron_manager = CronManager(max_routines=max_routines)

        except Exception as e:
            logger.warning(f"Could not load scheduler settings: {e}")
            _cron_manager = CronManager()

    return _cron_manager
