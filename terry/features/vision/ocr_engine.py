"""
OCR Engine - Terry v6.1
Universal OCR for text extraction from screen
"""
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import pyperclip
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """Universal OCR engine for text extraction."""

    def __init__(self, engine: str = "tesseract", languages: Optional[List[str]] = None):
        """
        Initialize OCR Engine.

        Args:
            engine: OCR engine to use ('tesseract' or 'apple_vision')
            languages: Languages to detect (e.g., ['eng', 'spa'])
        """
        self.engine = engine
        self.languages = languages or ['eng', 'spa']
        self._check_dependencies()

        logger.info(f"OCR Engine initialized: {engine}")

    def _check_dependencies(self):
        """Check if OCR dependencies are available."""
        if self.engine == "tesseract":
            try:
                result = subprocess.run(
                    ['tesseract', '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    logger.warning("Tesseract not found, OCR may not work")
                    logger.info("Install with: brew install tesseract")
            except FileNotFoundError:
                logger.warning("Tesseract not installed")
                logger.info("Install with: brew install tesseract")
            except Exception as e:
                logger.error(f"Error checking Tesseract: {e}")

    async def capture_screenshot(self) -> Optional[str]:
        """
        Capture screenshot of current screen.

        Returns:
            Path to screenshot file or None
        """
        try:
            # Create temp file
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"{temp_dir}/terry_ocr_{timestamp}.png"

            # Use macOS screencapture command
            result = subprocess.run(
                ['screencapture', '-x', screenshot_path],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0 and Path(screenshot_path).exists():
                logger.info(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                logger.error("Screenshot failed")
                return None

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

    async def extract_text(self, image_path: str) -> Optional[str]:
        """
        Extract text from image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text or None
        """
        if not Path(image_path).exists():
            logger.error(f"Image not found: {image_path}")
            return None

        if self.engine == "tesseract":
            return await self._extract_text_tesseract(image_path)
        elif self.engine == "apple_vision":
            return await self._extract_text_apple_vision(image_path)
        else:
            logger.error(f"Unknown OCR engine: {self.engine}")
            return None

    async def _extract_text_tesseract(self, image_path: str) -> Optional[str]:
        """
        Extract text using Tesseract OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text or None
        """
        try:
            # Build language parameter
            lang_param = '+'.join(self.languages)

            # Run tesseract
            result = subprocess.run(
                ['tesseract', image_path, 'stdout', '-l', lang_param],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                text = result.stdout.strip()
                logger.info(f"OCR extracted {len(text)} characters")
                return text if text else None
            else:
                logger.error(f"Tesseract error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Tesseract timeout")
            return None
        except Exception as e:
            logger.error(f"Error running Tesseract: {e}")
            return None

    async def _extract_text_apple_vision(self, image_path: str) -> Optional[str]:
        """
        Extract text using Apple Vision Framework.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text or None
        """
        try:
            # Use macOS Vision framework via AppleScript
            applescript = f'''
            use framework "Vision"
            use framework "AppKit"
            use scripting additions

            set theImage to current application's NSImage's alloc()'s initWithContentsOfFile:"{image_path}"
            set theCIImage to current application's CIImage's imageWithData:(theImage's TIFFRepresentation())

            set theRequest to current application's VNRecognizeTextRequest's alloc()'s init()
            set theHandler to current application's VNImageRequestHandler's alloc()'s initWithCIImage:theCIImage options:(missing value)

            theHandler's performRequests:{{theRequest}} |error|:(missing value)

            set theResults to theRequest's results()
            set theText to ""

            repeat with aResult in theResults
                set theText to theText & (aResult's text() as text) & linefeed
            end repeat

            return theText
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                text = result.stdout.strip()
                logger.info(f"Apple Vision extracted {len(text)} characters")
                return text if text else None
            else:
                logger.error(f"Apple Vision error: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error using Apple Vision: {e}")
            return None

    async def read_screen(self) -> Optional[str]:
        """
        Capture screenshot and extract text in one operation.

        Returns:
            Extracted text or None
        """
        # Capture screenshot
        screenshot_path = await self.capture_screenshot()
        if not screenshot_path:
            return None

        # Extract text
        text = await self.extract_text(screenshot_path)

        # Clean up temp file
        try:
            Path(screenshot_path).unlink()
        except Exception:
            pass

        return text

    async def read_and_copy(self) -> Optional[str]:
        """
        Read text from screen and copy to clipboard.

        Returns:
            Extracted text or None
        """
        text = await self.read_screen()

        if text:
            try:
                pyperclip.copy(text)
                logger.info("Text copied to clipboard")
            except Exception as e:
                logger.error(f"Error copying to clipboard: {e}")

        return text


# Singleton instance
_ocr_engine: Optional[OCREngine] = None


def get_ocr_engine() -> OCREngine:
    """
    Get the singleton OCREngine instance.

    Returns:
        OCREngine instance
    """
    global _ocr_engine

    if _ocr_engine is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("ocr", {})

            engine = config.get("engine", "tesseract")
            languages = config.get("languages", ["eng", "spa"])

            _ocr_engine = OCREngine(engine=engine, languages=languages)

        except Exception as e:
            logger.warning(f"Could not load OCR settings: {e}")
            _ocr_engine = OCREngine()

    return _ocr_engine
