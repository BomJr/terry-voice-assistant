"""
Configuration Settings Loader
Loads settings from settings.yaml and provides easy access
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Settings:
    """Settings manager that loads from YAML."""

    def __init__(self):
        self._settings: Optional[Dict[str, Any]] = None
        self._settings_file = Path(__file__).parent / "settings.yaml"

    def _load(self):
        """Load settings from YAML file."""
        if self._settings is None:
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    self._settings = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
                self._settings = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (can use dot notation like "llm.provider")
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        self._load()

        # Support dot notation
        keys = key.split('.')
        value = self._settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def __getitem__(self, key: str) -> Any:
        """Dict-like access."""
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return self.get(key) is not None

    def all(self) -> Dict[str, Any]:
        """Get all settings."""
        self._load()
        return self._settings.copy()


# Global settings instance
_settings_instance = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# Convenience alias
settings = get_settings()
