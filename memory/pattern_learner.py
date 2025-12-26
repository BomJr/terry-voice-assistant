"""
Pattern Learner - Terry v6.1
Detects and learns user behavioral patterns from command history
"""
from collections import defaultdict
from datetime import datetime, time
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class PatternLearner:
    """Learns user patterns from command history."""

    def __init__(self, patterns_file: Optional[str] = None):
        """
        Initialize Pattern Learner.

        Args:
            patterns_file: Path to patterns JSON file (default: ~/.terry/memory/patterns.json)
        """
        if patterns_file:
            self.patterns_file = Path(patterns_file)
        else:
            self.patterns_file = Path.home() / ".terry" / "memory" / "patterns.json"

        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = self._load_patterns()

        logger.info("Pattern Learner initialized")

    def record_command(self, command: str, timestamp: Optional[datetime] = None,
                       context: Optional[Dict[str, Any]] = None):
        """
        Record a command execution for pattern detection.

        Args:
            command: Command executed
            timestamp: When it was executed (default: now)
            context: Additional context (app opened, location, etc.)
        """
        if timestamp is None:
            timestamp = datetime.now()

        if context is None:
            context = {}

        hour = timestamp.hour
        weekday = timestamp.strftime("%A")
        time_of_day = self._get_time_of_day(hour)

        # Temporal patterns by hour
        if hour not in self.patterns['by_hour']:
            self.patterns['by_hour'][hour] = {}
        if command not in self.patterns['by_hour'][hour]:
            self.patterns['by_hour'][hour][command] = 0
        self.patterns['by_hour'][hour][command] += 1

        # Temporal patterns by weekday
        if weekday not in self.patterns['by_weekday']:
            self.patterns['by_weekday'][weekday] = {}
        if command not in self.patterns['by_weekday'][weekday]:
            self.patterns['by_weekday'][weekday][command] = 0
        self.patterns['by_weekday'][weekday][command] += 1

        # Temporal patterns by time of day
        if time_of_day not in self.patterns['by_time_of_day']:
            self.patterns['by_time_of_day'][time_of_day] = {}
        if command not in self.patterns['by_time_of_day'][time_of_day]:
            self.patterns['by_time_of_day'][time_of_day][command] = 0
        self.patterns['by_time_of_day'][time_of_day][command] += 1

        # Sequential patterns (command chains)
        if self.patterns['last_command']:
            pair = f"{self.patterns['last_command']} → {command}"
            if pair not in self.patterns['sequences']:
                self.patterns['sequences'][pair] = 0
            self.patterns['sequences'][pair] += 1

        # Update last command
        self.patterns['last_command'] = command

        # Context-based patterns (if app or location provided)
        if context.get('active_app'):
            app = context['active_app']
            if app not in self.patterns['by_app']:
                self.patterns['by_app'][app] = {}
            if command not in self.patterns['by_app'][app]:
                self.patterns['by_app'][app][command] = 0
            self.patterns['by_app'][app][command] += 1

        # Update total count
        if command not in self.patterns['total_counts']:
            self.patterns['total_counts'][command] = 0
        self.patterns['total_counts'][command] += 1

        self._save_patterns()

    def get_suggestions(self, current_time: Optional[datetime] = None,
                       context: Optional[Dict[str, Any]] = None,
                       min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """
        Get command suggestions based on learned patterns.

        Args:
            current_time: Current datetime (default: now)
            context: Current context (app, location, etc.)
            min_occurrences: Minimum times a pattern must occur to suggest

        Returns:
            List of suggestions with confidence scores
        """
        if current_time is None:
            current_time = datetime.now()

        if context is None:
            context = {}

        suggestions = []
        hour = current_time.hour
        weekday = current_time.strftime("%A")
        time_of_day = self._get_time_of_day(hour)

        # Check temporal patterns by hour
        hour_commands = self.patterns['by_hour'].get(hour, {})
        for command, count in hour_commands.items():
            if count >= min_occurrences:
                confidence = min(count / 10.0, 1.0)  # Cap at 1.0
                suggestions.append({
                    'command': command,
                    'reason': f'Usually at {hour}:00',
                    'confidence': confidence,
                    'type': 'temporal_hour',
                    'count': count
                })

        # Check patterns by weekday
        weekday_commands = self.patterns['by_weekday'].get(weekday, {})
        for command, count in weekday_commands.items():
            if count >= min_occurrences:
                # Check if already suggested by hour
                if not any(s['command'] == command for s in suggestions):
                    confidence = min(count / 8.0, 0.8)
                    suggestions.append({
                        'command': command,
                        'reason': f'Usually on {weekday}',
                        'confidence': confidence,
                        'type': 'temporal_weekday',
                        'count': count
                    })

        # Check patterns by time of day
        tod_commands = self.patterns['by_time_of_day'].get(time_of_day, {})
        for command, count in tod_commands.items():
            if count >= min_occurrences:
                if not any(s['command'] == command for s in suggestions):
                    confidence = min(count / 12.0, 0.9)
                    suggestions.append({
                        'command': command,
                        'reason': f'Usually in the {time_of_day}',
                        'confidence': confidence,
                        'type': 'temporal_time_of_day',
                        'count': count
                    })

        # Check sequential patterns based on last command
        if self.patterns['last_command']:
            for sequence, count in self.patterns['sequences'].items():
                if sequence.startswith(self.patterns['last_command'] + ' → '):
                    next_command = sequence.split(' → ')[1]
                    if count >= min_occurrences:
                        confidence = min(count / 5.0, 1.0)
                        suggestions.append({
                            'command': next_command,
                            'reason': f'Often follows "{self.patterns["last_command"]}"',
                            'confidence': confidence,
                            'type': 'sequential',
                            'count': count
                        })

        # Check app-based patterns
        if context.get('active_app'):
            app = context['active_app']
            app_commands = self.patterns['by_app'].get(app, {})
            for command, count in app_commands.items():
                if count >= min_occurrences:
                    if not any(s['command'] == command for s in suggestions):
                        confidence = min(count / 6.0, 0.85)
                        suggestions.append({
                            'command': command,
                            'reason': f'Common when using {app}',
                            'confidence': confidence,
                            'type': 'contextual_app',
                            'count': count
                        })

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        return suggestions

    def get_top_patterns(self, pattern_type: str = 'all',
                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top patterns of a specific type.

        Args:
            pattern_type: Type of pattern ('hour', 'weekday', 'sequence', 'app', 'all')
            limit: Maximum number of patterns to return

        Returns:
            List of top patterns
        """
        patterns = []

        if pattern_type in ['hour', 'all']:
            for hour, commands in self.patterns['by_hour'].items():
                for command, count in commands.items():
                    patterns.append({
                        'type': 'hour',
                        'key': f'{hour}:00',
                        'command': command,
                        'count': count
                    })

        if pattern_type in ['weekday', 'all']:
            for weekday, commands in self.patterns['by_weekday'].items():
                for command, count in commands.items():
                    patterns.append({
                        'type': 'weekday',
                        'key': weekday,
                        'command': command,
                        'count': count
                    })

        if pattern_type in ['sequence', 'all']:
            for sequence, count in self.patterns['sequences'].items():
                patterns.append({
                    'type': 'sequence',
                    'key': sequence,
                    'command': sequence,
                    'count': count
                })

        if pattern_type in ['app', 'all']:
            for app, commands in self.patterns['by_app'].items():
                for command, count in commands.items():
                    patterns.append({
                        'type': 'app',
                        'key': app,
                        'command': command,
                        'count': count
                    })

        # Sort by count
        patterns.sort(key=lambda x: x['count'], reverse=True)

        return patterns[:limit]

    def clear_patterns(self):
        """Clear all learned patterns."""
        self.patterns = self._init_patterns_structure()
        self._save_patterns()
        logger.info("All patterns cleared")

    def _get_time_of_day(self, hour: int) -> str:
        """
        Get time of day category from hour.

        Args:
            hour: Hour (0-23)

        Returns:
            Time of day category
        """
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def _init_patterns_structure(self) -> Dict:
        """Initialize empty patterns structure."""
        return {
            'by_hour': {},          # {hour: {command: count}}
            'by_weekday': {},       # {weekday: {command: count}}
            'by_time_of_day': {},   # {time_of_day: {command: count}}
            'sequences': {},        # {"cmd1 → cmd2": count}
            'by_app': {},          # {app_name: {command: count}}
            'total_counts': {},     # {command: total_count}
            'last_command': None,
            'version': '1.0'
        }

    def _load_patterns(self) -> Dict:
        """Load patterns from disk."""
        if self.patterns_file.exists():
            try:
                data = json.loads(self.patterns_file.read_text())
                logger.debug(f"Loaded {len(data.get('total_counts', {}))} pattern entries")
                return data
            except Exception as e:
                logger.error(f"Error loading patterns: {e}")

        return self._init_patterns_structure()

    def _save_patterns(self):
        """Save patterns to disk."""
        try:
            self.patterns_file.write_text(json.dumps(self.patterns, indent=2))
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")


# Singleton instance
_pattern_learner: Optional[PatternLearner] = None


def get_pattern_learner() -> PatternLearner:
    """
    Get the singleton PatternLearner instance.

    Returns:
        PatternLearner instance
    """
    global _pattern_learner

    if _pattern_learner is None:
        try:
            from config.settings import settings
            patterns_file = settings.get("pattern_learning", {}).get("patterns_file")
            _pattern_learner = PatternLearner(patterns_file=patterns_file)
        except Exception as e:
            logger.warning(f"Could not load settings for pattern learner: {e}")
            _pattern_learner = PatternLearner()

    return _pattern_learner
