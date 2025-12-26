"""
Plugin System - Terry v6.1
Load and execute custom plugins
"""
import importlib.util
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from utils.logger import get_logger

logger = get_logger(__name__)


class Plugin:
    """Base class for Terry plugins."""

    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize plugin.

        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.enabled = True

    def initialize(self):
        """Initialize plugin (called on load)."""
        pass

    def execute(self, command: str, params: Dict[str, Any]) -> Any:
        """
        Execute plugin command.

        Args:
            command: Command to execute
            params: Command parameters

        Returns:
            Command result
        """
        raise NotImplementedError("Plugin must implement execute()")

    def cleanup(self):
        """Cleanup plugin resources (called on unload)."""
        pass


class PluginSystem:
    """Manages Terry plugins."""

    def __init__(self, plugin_directory: Optional[str] = None, auto_discover: bool = True):
        """
        Initialize Plugin System.

        Args:
            plugin_directory: Directory containing plugins
            auto_discover: Automatically discover and load plugins
        """
        self.plugin_dir = Path(plugin_directory or str(Path.home() / ".terry" / "plugins"))
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: Dict[str, Plugin] = {}
        self.command_handlers: Dict[str, Callable] = {}

        if auto_discover:
            self.discover_plugins()

        logger.info("Plugin System initialized")

    def discover_plugins(self):
        """Discover and load plugins from plugin directory."""
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return

        # Find all .py files in plugin directory
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip private files

            try:
                self.load_plugin(plugin_file)
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_file}: {e}")

    def load_plugin(self, plugin_path: Path) -> bool:
        """
        Load a plugin from file.

        Args:
            plugin_path: Path to plugin file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(
                plugin_path.stem,
                plugin_path
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_path.stem] = module
                spec.loader.exec_module(module)

                # Look for Plugin class
                if hasattr(module, 'Plugin'):
                    plugin_class = getattr(module, 'Plugin')
                    plugin = plugin_class()

                    # Initialize plugin
                    plugin.initialize()

                    # Register plugin
                    self.plugins[plugin.name] = plugin

                    logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                    return True
                else:
                    logger.warning(f"Plugin file {plugin_path} has no Plugin class")
                    return False
            else:
                logger.error(f"Could not load spec for {plugin_path}")
                return False

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Cleanup plugin
            plugin.cleanup()

            # Remove from registry
            del self.plugins[plugin_name]

            logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def execute_plugin_command(self, plugin_name: str, command: str,
                               params: Dict[str, Any]) -> Any:
        """
        Execute a plugin command.

        Args:
            plugin_name: Plugin name
            command: Command to execute
            params: Command parameters

        Returns:
            Command result
        """
        if plugin_name not in self.plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return None

        plugin = self.plugins[plugin_name]

        if not plugin.enabled:
            logger.warning(f"Plugin disabled: {plugin_name}")
            return None

        try:
            result = plugin.execute(command, params)
            logger.debug(f"Executed {plugin_name}.{command}")
            return result

        except Exception as e:
            logger.error(f"Error executing plugin command: {e}")
            return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins.

        Returns:
            List of plugin info
        """
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'enabled': plugin.enabled
            }
            for plugin in self.plugins.values()
        ]

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False


# Singleton instance
_plugin_system: Optional[PluginSystem] = None


def get_plugin_system() -> PluginSystem:
    """
    Get the singleton PluginSystem instance.

    Returns:
        PluginSystem instance
    """
    global _plugin_system

    if _plugin_system is None:
        try:
            from config.settings import settings
            config = settings.get("plugins", {})

            plugin_dir = config.get("plugin_directory")
            auto_discover = config.get("auto_discover", True)

            _plugin_system = PluginSystem(
                plugin_directory=plugin_dir,
                auto_discover=auto_discover
            )

        except Exception as e:
            logger.warning(f"Could not load plugin system settings: {e}")
            _plugin_system = PluginSystem()

    return _plugin_system
