"""
Intelligent Suggestions - Terry v6.1
Proactive suggestions based on time, context, and learned patterns
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, time as dt_time
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class IntelligentSuggestions:
    """Generates intelligent suggestions based on multiple factors."""

    def __init__(self):
        """Initialize Intelligent Suggestions."""
        self.pattern_learner = None
        self.context_manager = None
        self._initialized = False

        logger.info("Intelligent Suggestions initialized")

    def initialize(self, pattern_learner=None, context_manager=None):
        """
        Initialize with pattern learner and context manager.

        Args:
            pattern_learner: PatternLearner instance
            context_manager: ContextManager instance
        """
        self.pattern_learner = pattern_learner
        self.context_manager = context_manager
        self._initialized = True
        logger.debug("Suggestions initialized with dependencies")

    def get_suggestions(self, current_time: Optional[datetime] = None,
                       max_suggestions: int = 3,
                       min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Get intelligent suggestions for the user.

        Args:
            current_time: Current time (default: now)
            max_suggestions: Maximum number of suggestions
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of suggestions sorted by relevance
        """
        if not self._initialized:
            logger.warning("Suggestions not fully initialized")
            return []

        if current_time is None:
            current_time = datetime.now()

        all_suggestions = []

        # 1. Time-based suggestions
        time_suggestions = self._get_time_based_suggestions(current_time)
        all_suggestions.extend(time_suggestions)

        # 2. Pattern-based suggestions (from pattern learner)
        if self.pattern_learner:
            pattern_suggestions = self._get_pattern_based_suggestions(current_time)
            all_suggestions.extend(pattern_suggestions)

        # 3. Context-based suggestions
        if self.context_manager:
            context_suggestions = self._get_context_based_suggestions()
            all_suggestions.extend(context_suggestions)

        # Filter by confidence
        filtered = [s for s in all_suggestions if s['confidence'] >= min_confidence]

        # Remove duplicates (keep highest confidence)
        unique = {}
        for suggestion in filtered:
            cmd = suggestion['command']
            if cmd not in unique or suggestion['confidence'] > unique[cmd]['confidence']:
                unique[cmd] = suggestion

        # Sort by confidence
        sorted_suggestions = sorted(unique.values(),
                                   key=lambda x: x['confidence'],
                                   reverse=True)

        return sorted_suggestions[:max_suggestions]

    def _get_time_based_suggestions(self, current_time: datetime) -> List[Dict[str, Any]]:
        """
        Get suggestions based on time of day.

        Args:
            current_time: Current datetime

        Returns:
            List of time-based suggestions
        """
        suggestions = []
        hour = current_time.hour
        weekday = current_time.strftime("%A")

        # Morning routines (7-9 AM)
        if 7 <= hour < 9:
            if weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                suggestions.append({
                    'command': 'modo trabajo',
                    'reason': 'Start your work day',
                    'confidence': 0.75,
                    'type': 'time_based',
                    'trigger': 'morning_weekday'
                })

        # Lunch time (12-2 PM)
        elif 12 <= hour < 14:
            suggestions.append({
                'command': 'pon música relajante',
                'reason': 'Lunch time music',
                'confidence': 0.65,
                'type': 'time_based',
                'trigger': 'lunch_time'
            })

        # Afternoon focus (2-5 PM)
        elif 14 <= hour < 17:
            if weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                suggestions.append({
                    'command': 'modo focus',
                    'reason': 'Afternoon focus time',
                    'confidence': 0.70,
                    'type': 'time_based',
                    'trigger': 'afternoon_weekday'
                })

        # Evening (6-9 PM)
        elif 18 <= hour < 21:
            suggestions.append({
                'command': 'modo descanso',
                'reason': 'Wind down for the evening',
                'confidence': 0.68,
                'type': 'time_based',
                'trigger': 'evening'
            })

        # Night time (9 PM - midnight)
        elif 21 <= hour < 24:
            suggestions.append({
                'command': 'buenas noches',
                'reason': 'Bedtime routine',
                'confidence': 0.72,
                'type': 'time_based',
                'trigger': 'night'
            })

        return suggestions

    def _get_pattern_based_suggestions(self, current_time: datetime) -> List[Dict[str, Any]]:
        """
        Get suggestions based on learned patterns.

        Args:
            current_time: Current datetime

        Returns:
            List of pattern-based suggestions
        """
        if not self.pattern_learner:
            return []

        suggestions = []

        try:
            # Get suggestions from pattern learner
            pattern_suggestions = self.pattern_learner.get_suggestions(
                current_time=current_time,
                min_occurrences=3
            )

            # Convert to our format
            for ps in pattern_suggestions:
                suggestions.append({
                    'command': ps['command'],
                    'reason': ps['reason'],
                    'confidence': ps['confidence'],
                    'type': 'pattern_based',
                    'subtype': ps['type'],
                    'count': ps.get('count', 0)
                })

        except Exception as e:
            logger.error(f"Error getting pattern suggestions: {e}")

        return suggestions

    def _get_context_based_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get suggestions based on current context.

        Returns:
            List of context-based suggestions
        """
        if not self.context_manager:
            return []

        suggestions = []

        try:
            # Get context
            context = self.context_manager.get_context_for_command("")

            # If music is playing, suggest next/pause
            if context.get('has_music_context'):
                suggestions.append({
                    'command': 'siguiente',
                    'reason': 'Music is playing',
                    'confidence': 0.80,
                    'type': 'context_based',
                    'trigger': 'music_playing'
                })

            # If an app was recently opened, suggest related actions
            if context.get('has_app_context'):
                app = context.get('entities', {}).get('app', {}).get('name')
                if app == 'vscode' or app == 'code':
                    suggestions.append({
                        'command': 'pon música de trabajo',
                        'reason': f'VS Code is open',
                        'confidence': 0.75,
                        'type': 'context_based',
                        'trigger': 'app_vscode'
                    })

            # Based on recent commands
            recent = context.get('recent_commands', [])
            if recent:
                last_cmd = recent[-1].lower()

                # If last command was volume related, suggest related actions
                if 'volumen' in last_cmd or 'volume' in last_cmd:
                    if 'sube' in last_cmd or 'up' in last_cmd:
                        suggestions.append({
                            'command': 'baja volumen',
                            'reason': 'You just increased volume',
                            'confidence': 0.65,
                            'type': 'context_based',
                            'trigger': 'recent_volume_up'
                        })

        except Exception as e:
            logger.error(f"Error getting context suggestions: {e}")

        return suggestions

    def should_show_suggestions(self, idle_time_seconds: float = 0) -> bool:
        """
        Determine if suggestions should be shown.

        Args:
            idle_time_seconds: Seconds since last user interaction

        Returns:
            True if suggestions should be shown
        """
        # Show suggestions after 30 seconds of idle time
        if idle_time_seconds > 30:
            return True

        # Or show at specific times of day
        hour = datetime.now().hour

        # Show suggestions at the start of key times
        key_hours = [7, 9, 12, 14, 18, 21]  # Start of day, work, lunch, afternoon, evening, night
        if hour in key_hours:
            return True

        return False


# Singleton instance
_intelligent_suggestions: Optional[IntelligentSuggestions] = None


def get_intelligent_suggestions() -> IntelligentSuggestions:
    """
    Get the singleton IntelligentSuggestions instance.

    Returns:
        IntelligentSuggestions instance
    """
    global _intelligent_suggestions

    if _intelligent_suggestions is None:
        _intelligent_suggestions = IntelligentSuggestions()

    return _intelligent_suggestions
