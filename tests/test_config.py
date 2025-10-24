"""Tests for config module."""

import json
import tempfile
from pathlib import Path

import pytest

from jst_django.config import ConfigManager
from jst_django.exceptions import ConfigurationError


class TestConfigManager:
    """Test ConfigManager class."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config = {
                "dirs": {"apps": "./apps/"},
                "import_path": "myapp.",
            }
            json.dump(config, f)
            f.flush()  # Ensure content is written
        yield Path(f.name)
        Path(f.name).unlink()

    def test_load_default_config(self):
        """Test loading default config when file doesn't exist."""
        config_manager = ConfigManager(Path("nonexistent.json"))
        config = config_manager.load()
        assert "dirs" in config
        assert "import_path" in config

    def test_load_custom_config(self, temp_config_file):
        """Test loading custom config."""
        config_manager = ConfigManager(temp_config_file)
        config = config_manager.load()
        assert config["dirs"]["apps"] == "./apps/"
        assert config["import_path"] == "myapp."

    def test_get_config_value(self, temp_config_file):
        """Test getting config value."""
        config_manager = ConfigManager(temp_config_file)
        assert config_manager.get("dirs.apps") == "./apps/"
        assert config_manager.get("import_path") == "myapp."
        assert config_manager.get("nonexistent", "default") == "default"

    def test_save_config(self):
        """Test saving config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_path = Path(f.name)

        try:
            config_manager = ConfigManager(config_path)
            new_config = {"dirs": {"apps": "./new_apps/"}}
            config_manager.save(new_config)

            # Load and verify
            with open(config_path, "r") as f:
                saved_config = json.load(f)
            assert saved_config["dirs"]["apps"] == "./new_apps/"
        finally:
            config_path.unlink()

    def test_validate_config_invalid_type(self):
        """Test config validation with invalid type."""
        config_manager = ConfigManager()
        with pytest.raises(ConfigurationError):
            config_manager._validate_config("invalid")

    def test_validate_config_invalid_dirs(self):
        """Test config validation with invalid dirs."""
        config_manager = ConfigManager()
        with pytest.raises(ConfigurationError):
            config_manager._validate_config({"dirs": "invalid"})
