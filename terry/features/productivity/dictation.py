"""
Universal Dictation - Terry v6.1
Type voice transcription to any active application
"""
import time
from typing import Optional
import pyautogui
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class UniversalDictation:
    """Universal dictation to active application."""

    def __init__(self, auto_punctuation: bool = True, typing_interval: float = 0.01):
        """
        Initialize Universal Dictation.

        Args:
            auto_punctuation: Automatically add punctuation
            typing_interval: Interval between keystrokes (seconds)
        """
        self.auto_punctuation = auto_punctuation
        self.typing_interval = typing_interval
        self.is_dictating = False

        # Configure pyautogui
        pyautogui.PAUSE = typing_interval

        logger.info("Universal Dictation initialized")

    def start_dictation(self):
        """Start dictation mode."""
        self.is_dictating = True
        logger.info("Dictation mode started")

    def stop_dictation(self):
        """Stop dictation mode."""
        self.is_dictating = False
        logger.info("Dictation mode stopped")

    def is_dictation_active(self) -> bool:
        """Check if dictation is active."""
        return self.is_dictating

    def type_text(self, text: str, add_newline: bool = False) -> bool:
        """
        Type text to the active application.

        Args:
            text: Text to type
            add_newline: Add newline after text

        Returns:
            True if successful, False otherwise
        """
        try:
            # Apply auto-punctuation if enabled
            if self.auto_punctuation:
                text = self._apply_auto_punctuation(text)

            # Type the text
            pyautogui.write(text, interval=self.typing_interval)

            # Add newline if requested
            if add_newline:
                pyautogui.press('enter')

            logger.info(f"Typed {len(text)} characters")
            return True

        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False

    def insert_text(self, text: str) -> bool:
        """
        Insert text at current cursor position (alias for type_text).

        Args:
            text: Text to insert

        Returns:
            True if successful, False otherwise
        """
        return self.type_text(text, add_newline=False)

    def type_command(self, command: str) -> bool:
        """
        Execute keyboard command/shortcut.

        Args:
            command: Command like 'enter', 'backspace', 'ctrl+c', etc.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle combinations like 'ctrl+c'
            if '+' in command:
                keys = command.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(command)

            logger.debug(f"Executed keyboard command: {command}")
            return True

        except Exception as e:
            logger.error(f"Error executing keyboard command: {e}")
            return False

    def _apply_auto_punctuation(self, text: str) -> str:
        """
        Apply automatic punctuation to text.

        Args:
            text: Input text

        Returns:
            Text with punctuation
        """
        # Basic auto-punctuation rules
        text = text.strip()

        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        # Add period at end if no punctuation
        if text and text[-1] not in '.!?,:;':
            # Check if it's a question
            question_words = ['qué', 'quién', 'cuándo', 'dónde', 'cómo', 'por qué',
                            'what', 'who', 'when', 'where', 'how', 'why']
            if any(text.lower().startswith(word) for word in question_words):
                text += '?'
            else:
                text += '.'

        return text

    def delete_last_word(self) -> bool:
        """
        Delete the last typed word.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ctrl+Backspace deletes last word on most systems
            pyautogui.hotkey('ctrl', 'backspace')
            logger.debug("Deleted last word")
            return True

        except Exception as e:
            logger.error(f"Error deleting word: {e}")
            return False

    def delete_last_sentence(self) -> bool:
        """
        Delete the last typed sentence (approximation).

        Returns:
            True if successful, False otherwise
        """
        try:
            # Select and delete approximately one sentence
            # This is an approximation, actual behavior depends on app
            for _ in range(3):  # Delete ~3 words
                pyautogui.hotkey('ctrl', 'backspace')
                time.sleep(0.05)

            logger.debug("Deleted last sentence (approximation)")
            return True

        except Exception as e:
            logger.error(f"Error deleting sentence: {e}")
            return False

    def new_line(self) -> bool:
        """
        Insert a new line.

        Returns:
            True if successful, False otherwise
        """
        return self.type_command('enter')

    def new_paragraph(self) -> bool:
        """
        Insert a new paragraph (double newline).

        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.press('enter')
            pyautogui.press('enter')
            return True
        except Exception as e:
            logger.error(f"Error creating paragraph: {e}")
            return False


# Singleton instance
_dictation: Optional[UniversalDictation] = None


def get_dictation() -> UniversalDictation:
    """
    Get the singleton UniversalDictation instance.

    Returns:
        UniversalDictation instance
    """
    global _dictation

    if _dictation is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("dictation", {})

            auto_punctuation = config.get("auto_punctuation", True)
            _dictation = UniversalDictation(auto_punctuation=auto_punctuation)

        except Exception as e:
            logger.warning(f"Could not load dictation settings: {e}")
            _dictation = UniversalDictation()

    return _dictation
