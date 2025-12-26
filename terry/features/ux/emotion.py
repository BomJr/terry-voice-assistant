"""
Frustration Detector - Terry v6.1
Detect user frustration from repeated commands and patterns
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import deque
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class FrustrationDetector:
    """Detects user frustration patterns."""

    def __init__(self, sensitivity: float = 0.5, window_minutes: int = 5):
        """
        Initialize Frustration Detector.

        Args:
            sensitivity: Detection sensitivity (0-1, higher = more sensitive)
            window_minutes: Time window for pattern detection
        """
        self.sensitivity = sensitivity
        self.window_minutes = window_minutes

        # Track recent commands
        self.command_history: deque = deque(maxlen=20)

        # Track failed commands
        self.failed_commands: deque = deque(maxlen=10)

        # Frustration indicators
        self.frustration_keywords = [
            "no funciona", "no sirve", "mal", "error", "ayuda",
            "doesn't work", "broken", "help", "fix"
        ]

        self.repetition_keywords = [
            "de nuevo", "otra vez", "repite", "again", "repeat"
        ]

        logger.info("Frustration Detector initialized")

    def record_command(self, command: str, success: bool, timestamp: Optional[datetime] = None):
        """
        Record a command execution.

        Args:
            command: Command text
            success: Whether command succeeded
            timestamp: Command timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        record = {
            'command': command.lower(),
            'success': success,
            'timestamp': timestamp
        }

        self.command_history.append(record)

        if not success:
            self.failed_commands.append(record)

    def detect_frustration(self) -> Dict[str, Any]:
        """
        Detect frustration based on patterns.

        Returns:
            Dict with frustration level and reasons
        """
        frustration_score = 0.0
        reasons = []

        # Check for frustration keywords
        recent_commands = [r['command'] for r in self.command_history]
        recent_text = ' '.join(recent_commands[-5:])  # Last 5 commands

        if any(keyword in recent_text for keyword in self.frustration_keywords):
            frustration_score += 0.3
            reasons.append("frustration_keywords")

        # Check for repetition
        if len(self.command_history) >= 3:
            last_3 = [r['command'] for r in list(self.command_history)[-3:]]
            if len(set(last_3)) == 1:  # Same command 3 times
                frustration_score += 0.4
                reasons.append("repeated_command")

        # Check for failed commands
        cutoff_time = datetime.now() - timedelta(minutes=self.window_minutes)
        recent_failures = [
            r for r in self.failed_commands
            if r['timestamp'] > cutoff_time
        ]

        if len(recent_failures) >= 3:
            frustration_score += 0.3
            reasons.append("multiple_failures")

        # Check for "otra vez" / "again" pattern
        if any(keyword in recent_text for keyword in self.repetition_keywords):
            frustration_score += 0.2
            reasons.append("repetition_keywords")

        # Normalize to 0-1
        frustration_score = min(frustration_score, 1.0)

        # Apply sensitivity
        frustration_score = frustration_score * (0.5 + self.sensitivity * 0.5)

        is_frustrated = frustration_score >= 0.5

        logger.debug(f"Frustration score: {frustration_score:.2f}, reasons: {reasons}")

        return {
            'frustrated': is_frustrated,
            'score': frustration_score,
            'reasons': reasons,
            'suggestion': self._get_suggestion(reasons) if is_frustrated else None
        }

    def _get_suggestion(self, reasons: List[str]) -> str:
        """
        Get helpful suggestion based on frustration reasons.

        Args:
            reasons: List of frustration reasons

        Returns:
            Helpful suggestion
        """
        if 'repeated_command' in reasons:
            return "Parece que tienes problemas con ese comando. ¿Puedo ayudarte de otra forma?"

        if 'multiple_failures' in reasons:
            return "Veo que varios comandos fallaron. ¿Quieres que revise la configuración?"

        if 'frustration_keywords' in reasons:
            return "Entiendo que estás frustrado. ¿Qué puedo hacer para ayudarte?"

        return "¿Necesitas ayuda con algo específico?"

    def reset(self):
        """Reset frustration detection state."""
        self.command_history.clear()
        self.failed_commands.clear()
        logger.debug("Frustration detector reset")


# Singleton instance
_frustration_detector: Optional[FrustrationDetector] = None


def get_frustration_detector() -> FrustrationDetector:
    """
    Get the singleton FrustrationDetector instance.

    Returns:
        FrustrationDetector instance
    """
    global _frustration_detector

    if _frustration_detector is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("frustration_detection", {})

            sensitivity = config.get("sensitivity", 0.5)
            _frustration_detector = FrustrationDetector(sensitivity=sensitivity)

        except Exception as e:
            logger.warning(f"Could not load frustration detection settings: {e}")
            _frustration_detector = FrustrationDetector()

    return _frustration_detector
