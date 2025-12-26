"""
VS Code Control - Terry v6.1
Control VS Code via CLI and AppleScript
"""
import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class VSCodeControl:
    """Controls VS Code via CLI."""

    def __init__(self, code_path: str = "/usr/local/bin/code"):
        """
        Initialize VS Code Control.

        Args:
            code_path: Path to VS Code CLI
        """
        self.code_path = code_path
        self._check_vscode()

        logger.info("VS Code Control initialized")

    def _check_vscode(self):
        """Check if VS Code CLI is available."""
        try:
            result = subprocess.run(
                [self.code_path, '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("VS Code CLI found")
            else:
                logger.warning("VS Code CLI not found at {self.code_path}")
        except FileNotFoundError:
            logger.warning("VS Code CLI not found. Install from Command Palette > Shell Command: Install 'code' command in PATH")
        except Exception as e:
            logger.error(f"Error checking VS Code: {e}")

    def open_file(self, file_path: str) -> bool:
        """
        Open file in VS Code.

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            expanded_path = os.path.expanduser(file_path)

            result = subprocess.run(
                [self.code_path, expanded_path],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"Opened file in VS Code: {file_path}")
                return True
            else:
                logger.error(f"Error opening file: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error opening file in VS Code: {e}")
            return False

    def open_folder(self, folder_path: str) -> bool:
        """
        Open folder in VS Code.

        Args:
            folder_path: Path to folder

        Returns:
            True if successful, False otherwise
        """
        try:
            expanded_path = os.path.expanduser(folder_path)

            result = subprocess.run(
                [self.code_path, expanded_path],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"Opened folder in VS Code: {folder_path}")
                return True
            else:
                logger.error(f"Error opening folder: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error opening folder in VS Code: {e}")
            return False

    def run_command(self, command: str) -> bool:
        """
        Run VS Code command.

        Args:
            command: Command to run (e.g., 'workbench.action.files.save')

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use AppleScript to run VS Code commands
            applescript = f'''
            tell application "Visual Studio Code"
                activate
            end tell

            tell application "System Events"
                keystroke "p" using {{command down, shift down}}
                delay 0.3
                keystroke "{command}"
                delay 0.2
                keystroke return
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"Executed VS Code command: {command}")
                return True
            else:
                logger.error(f"Error running command: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error running VS Code command: {e}")
            return False

    def run_terminal_command(self, command: str) -> bool:
        """
        Run command in VS Code integrated terminal.

        Args:
            command: Terminal command to run

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use AppleScript to type in VS Code terminal
            applescript = f'''
            tell application "Visual Studio Code"
                activate
            end tell

            tell application "System Events"
                -- Open terminal with Ctrl+`
                keystroke "`" using {{control down}}
                delay 0.5
                keystroke "{command}"
                keystroke return
            end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"Executed terminal command: {command}")
                return True
            else:
                logger.error(f"Error running terminal command: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error running terminal command: {e}")
            return False

    def run_tests(self) -> bool:
        """Run tests in VS Code."""
        return self.run_terminal_command("npm test")

    def git_status(self) -> bool:
        """Show git status."""
        return self.run_terminal_command("git status")

    def git_commit(self, message: str) -> bool:
        """Commit changes with message."""
        return self.run_terminal_command(f'git add . && git commit -m "{message}"')

    def git_push(self) -> bool:
        """Push changes."""
        return self.run_terminal_command("git push")


# Singleton instance
_vscode_control: Optional[VSCodeControl] = None


def get_vscode_control() -> VSCodeControl:
    """
    Get the singleton VSCodeControl instance.

    Returns:
        VSCodeControl instance
    """
    global _vscode_control

    if _vscode_control is None:
        try:
            from config.settings import settings
            config = settings.get("ide_control", {})

            code_path = config.get("vscode_path", "/usr/local/bin/code")
            _vscode_control = VSCodeControl(code_path=code_path)

        except Exception as e:
            logger.warning(f"Could not load IDE settings: {e}")
            _vscode_control = VSCodeControl()

    return _vscode_control
