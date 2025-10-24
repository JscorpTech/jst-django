"""Base utility classes and functions for jst-django."""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Union

from rich import print

from jst_django.config import ConfigManager
from jst_django.exceptions import ConfigurationError
from jst_django.utils.logger import logger


class Jst:
    """Main jst utility class for configuration management."""

    def __init__(self):
        """Initialize Jst utility."""
        self.base_dir = Path.cwd()
        self.config_manager = ConfigManager()
        self.default_config = {
            "dirs": {
                "apps": "./",
                "locale": "./locale/",
            },
            "stubs": {
                "admin": "django/admin.stub",
            },
            "import_path": "core.apps.",
        }

    def _check_config(self) -> bool:
        """
        Check if config file exists.

        Returns:
            True if config file exists
        """
        return self.config_manager.config_path.exists()

    def make_config(self) -> None:
        """
        Create config file.

        Raises:
            ConfigurationError: If config file already exists
        """
        try:
            if self._check_config():
                logger.error("Config file already exists")
                raise ConfigurationError("Config file already exists")

            self.config_manager.save(self.default_config)
            logger.info("Config file created successfully")
            print("[bold green]Config yaratildi.[/bold green]")

        except Exception as e:
            logger.exception("Failed to create config file")
            raise ConfigurationError("Failed to create config file", details=str(e))

    def load_config(self) -> dict:
        """
        Load config file.

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If config file not found or invalid
        """
        try:
            if not self._check_config():
                logger.warning("Config file not found, using defaults")
                return self.default_config

            return self.config_manager.load()

        except Exception as e:
            logger.exception("Failed to load config file")
            raise ConfigurationError("Failed to load config file", details=str(e))

    def requirements(self) -> None:
        """
        Display requirements file content.

        Raises:
            FileNotFoundError: If requirements stub file not found
        """
        try:
            requirements_path = Path(__file__).parent.parent / "stubs" / "requirements.txt.stub"

            if not requirements_path.exists():
                logger.error(f"Requirements file not found: {requirements_path}")
                raise FileNotFoundError(f"Requirements file not found: {requirements_path}")

            with open(requirements_path, "r", encoding="utf-8") as file:
                print(file.read())

        except Exception as e:
            logger.exception("Failed to display requirements")
            raise


class Code:
    """Code formatting and manipulation utilities."""

    def __init__(self):
        """Initialize Code utility."""
        pass

    @staticmethod
    def format_code(file_path: str) -> None:
        """
        Format code using black and isort.

        Args:
            file_path: Path to file to format

        Raises:
            FileNotFoundError: If file not found
        """
        from jst_django.utils.code import Code as CodeFormatter

        try:
            CodeFormatter.format_code(file_path)
        except Exception as e:
            logger.error(f"Failed to format code: {file_path}")
            logger.exception(e)
            raise


class File:
    """File operation utilities."""

    def __init__(self):
        """Initialize File utility."""
        pass

    @staticmethod
    def mkdir(path: Union[str, Path]) -> None:
        """
        Create directory if not exists.

        Args:
            path: Directory path to create
        """
        from jst_django.utils.file import File as FileUtil

        FileUtil.mkdir(path)


def cancel(message: str = "Operation cancelled") -> None:
    """
    Cancel operation and exit.

    Args:
        message: Message to display before exit
    """
    logger.warning(message)
    print(f"[bold yellow]{message}[/bold yellow]")
    sys.exit(0)


def get_progress():
    """
    Get progress context manager.

    Returns:
        Progress context manager
    """
    from jst_django.utils.progress import get_progress as get_prog

    return get_prog()
