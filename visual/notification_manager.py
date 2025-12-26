"""
Visual Notification Manager - Terry v6.1
Shows macOS notifications for all Terry responses
"""
import subprocess
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Manages macOS notifications for Terry responses."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._check_pync()

    def _check_pync(self):
        """Check if pync is available."""
        try:
            import pync
            self.pync = pync
            logger.info("pync library loaded successfully")
        except ImportError:
            logger.warning("pync not installed, notifications disabled")
            self.enabled = False
            self.pync = None

    def show(self, message: str, title: str = "Terry",
             subtitle: Optional[str] = None, sound: bool = False):
        """
        Show macOS notification.

        Args:
            message: Notification message
            title: Notification title (default: "Terry")
            subtitle: Optional subtitle
            sound: Play sound with notification
        """
        if not self.enabled or not self.pync:
            logger.debug(f"Notification disabled or pync unavailable: {message}")
            return

        try:
            # Show notification with pync
            self.pync.notify(
                message,
                title=title,
                subtitle=subtitle,
                sound="default" if sound else None,
                # Use Terry's icon (generic app icon for now)
                appIcon="/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/AlertStopIcon.icns"
            )
            logger.debug(f"Notification shown: {message}")

        except Exception as e:
            logger.error(f"Notification error: {e}")

    def enable(self):
        """Enable notifications."""
        self.enabled = True
        logger.info("Notifications enabled")

    def disable(self):
        """Disable notifications."""
        self.enabled = False
        logger.info("Notifications disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self.enabled and self.pync is not None


# Singleton instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """
    Get the singleton NotificationManager instance.

    Returns:
        NotificationManager instance
    """
    global _notification_manager

    if _notification_manager is None:
        # Try to load from settings
        try:
            from config.settings import settings
            enabled = settings.get("visual_notifications", {}).get("enabled", True)
            _notification_manager = NotificationManager(enabled=enabled)
        except Exception as e:
            logger.warning(f"Could not load settings for notifications: {e}")
            _notification_manager = NotificationManager(enabled=True)

    return _notification_manager


def show_notification(message: str, title: str = "Terry",
                     subtitle: Optional[str] = None, sound: bool = False):
    """
    Convenience function to show a notification.

    Args:
        message: Notification message
        title: Notification title
        subtitle: Optional subtitle
        sound: Play sound with notification
    """
    manager = get_notification_manager()
    manager.show(message, title, subtitle, sound)
