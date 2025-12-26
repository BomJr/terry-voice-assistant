"""
Barge-in - Terry v6.1
Interrupt Terry while speaking
"""
import threading
from typing import Optional, List
from utils.logger import get_logger

logger = get_logger(__name__)


class BargeInManager:
    """Manages interruption of Terry's speech."""

    def __init__(self, interrupt_keywords: Optional[List[str]] = None):
        """
        Initialize Barge-in Manager.

        Args:
            interrupt_keywords: Keywords that trigger interruption
        """
        self.interrupt_keywords = interrupt_keywords or ["cancela", "para", "stop", "cancel"]
        self.is_speaking = False
        self.interrupt_requested = False
        self.speech_lock = threading.Lock()

        logger.info("Barge-in Manager initialized")

    def start_speaking(self):
        """Signal that Terry started speaking."""
        with self.speech_lock:
            self.is_speaking = True
            self.interrupt_requested = False
        logger.debug("Started speaking")

    def stop_speaking(self):
        """Signal that Terry stopped speaking."""
        with self.speech_lock:
            self.is_speaking = False
            self.interrupt_requested = False
        logger.debug("Stopped speaking")

    def request_interrupt(self):
        """Request interruption of current speech."""
        with self.speech_lock:
            if self.is_speaking:
                self.interrupt_requested = True
                logger.info("Interrupt requested")
                return True
            return False

    def should_interrupt(self) -> bool:
        """Check if interruption was requested."""
        with self.speech_lock:
            return self.interrupt_requested

    def is_interrupt_keyword(self, text: str) -> bool:
        """
        Check if text contains interrupt keyword.

        Args:
            text: Text to check

        Returns:
            True if contains interrupt keyword
        """
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in self.interrupt_keywords)

    def reset(self):
        """Reset interrupt state."""
        with self.speech_lock:
            self.is_speaking = False
            self.interrupt_requested = False
        logger.debug("Barge-in reset")


# Singleton instance
_barge_in: Optional[BargeInManager] = None


def get_barge_in() -> BargeInManager:
    """
    Get the singleton BargeInManager instance.

    Returns:
        BargeInManager instance
    """
    global _barge_in

    if _barge_in is None:
        try:
            from config.settings import settings
            config = settings.get("barge_in", {})

            interrupt_keywords = config.get("interrupt_keywords", ["cancela", "para", "stop", "cancel"])
            _barge_in = BargeInManager(interrupt_keywords=interrupt_keywords)

        except Exception as e:
            logger.warning(f"Could not load barge-in settings: {e}")
            _barge_in = BargeInManager()

    return _barge_in
