"""Configuration management for jst-django."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from jst_django.constants import (DEFAULT_ADMIN_PATH, DEFAULT_APPS_PATH,
                                  DEFAULT_FILTERS_PATH, DEFAULT_FORMS_PATH,
                                  DEFAULT_IMPORT_PATH, DEFAULT_MODELS_PATH,
                                  DEFAULT_PERMISSIONS_PATH,
                                  DEFAULT_SERIALIZERS_PATH,
                                  DEFAULT_SIGNALS_PATH, DEFAULT_TESTS_PATH,
                                  DEFAULT_TRANSLATION_PATH,
                                  DEFAULT_VALIDATORS_PATH, DEFAULT_VIEWS_PATH,
                                  STUB_FILES)
from jst_django.exceptions import ConfigurationError


class ConfigManager:
    """Manage jst-django configuration."""

    CONFIG_FILE_NAME = "jst.json"
    DEFAULT_CONFIG = {
        "dirs": {
            "apps": DEFAULT_APPS_PATH,
            "models": DEFAULT_MODELS_PATH,
            "serializers": DEFAULT_SERIALIZERS_PATH,
            "views": DEFAULT_VIEWS_PATH,
            "permissions": DEFAULT_PERMISSIONS_PATH,
            "admin": DEFAULT_ADMIN_PATH,
            "tests": DEFAULT_TESTS_PATH,
            "translation": DEFAULT_TRANSLATION_PATH,
            "validators": DEFAULT_VALIDATORS_PATH,
            "forms": DEFAULT_FORMS_PATH,
            "filters": DEFAULT_FILTERS_PATH,
            "signals": DEFAULT_SIGNALS_PATH,
        },
        "import_path": DEFAULT_IMPORT_PATH,
        "stubs": STUB_FILES,
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file. If None, searches in current directory.
        """
        self.config_path = config_path or Path.cwd() / self.CONFIG_FILE_NAME
        self._config: Optional[Dict[str, Any]] = None
        self._cache: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If configuration file is invalid
        """
        if self._config is not None:
            return self._config

        try:
            if not self.config_path.exists():
                self._config = self.DEFAULT_CONFIG.copy()
                return self._config

            with open(self.config_path, "r", encoding="utf-8") as file:
                loaded_config = json.load(file)

            # Merge with defaults
            self._config = {**self.DEFAULT_CONFIG, **loaded_config}

            # Validate configuration
            self._validate_config(self._config)

            return self._config

        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {self.config_path}",
                details=str(e),
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from {self.config_path}",
                details=str(e),
            )

    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save

        Raises:
            ConfigurationError: If save operation fails
        """
        try:
            self._validate_config(config)

            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=2, ensure_ascii=False)

            self._config = config
            self._cache.clear()

        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration to {self.config_path}",
                details=str(e),
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation, e.g., 'dirs.apps')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        config = self.load()

        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Support dot notation
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        # Cache the result
        self._cache[key] = value
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        config = self.load()

        # Support dot notation
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save(config)

    def get_path(self, module: str) -> str:
        """
        Get path for a specific module.

        Args:
            module: Module name (e.g., 'model', 'view')

        Returns:
            Path string
        """
        return self.get(f"dirs.{module}s", f"{module}s/")

    def get_apps_path(self) -> str:
        """
        Get apps directory path.

        Returns:
            Apps path string
        """
        return self.get("dirs.apps", DEFAULT_APPS_PATH)

    def get_import_path(self) -> str:
        """
        Get base import path.

        Returns:
            Import path string
        """
        return self.get("import_path", DEFAULT_IMPORT_PATH)

    def get_stub_file(self, stub_name: str) -> str:
        """
        Get stub file name for a module.

        Args:
            stub_name: Stub name

        Returns:
            Stub file name
        """
        return self.get(f"stubs.{stub_name}", STUB_FILES.get(stub_name, f"{stub_name}.stub"))

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        """
        Validate configuration structure.

        Args:
            config: Configuration to validate

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")

        # Validate required keys
        if "dirs" in config and not isinstance(config["dirs"], dict):
            raise ConfigurationError("'dirs' must be a dictionary")

        if "stubs" in config and not isinstance(config["stubs"], dict):
            raise ConfigurationError("'stubs' must be a dictionary")

        if "import_path" in config and not isinstance(config["import_path"], str):
            raise ConfigurationError("'import_path' must be a string")

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()

    def reload(self) -> Dict[str, Any]:
        """
        Reload configuration from file.

        Returns:
            Reloaded configuration
        """
        self._config = None
        self._cache.clear()
        return self.load()
