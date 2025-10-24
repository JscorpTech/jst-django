"""Logging configuration for jst-django."""

import logging
import sys
from typing import Optional

import colorlog


class Logger:
    """Centralized logger for jst-django."""

    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self, name: str = "jst-django", level: int = logging.INFO) -> None:
        """
        Setup logger with colored output.

        Args:
            name: Logger name
            level: Logging level
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        # Prevent duplicate handlers
        if self._logger.handlers:
            return

        # Console handler with colors
        handler = colorlog.StreamHandler(sys.stdout)
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )
        )
        self._logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        """
        Get logger instance.

        Returns:
            Logger instance
        """
        return self._logger

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, exc_info=True, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, *args, exc_info=exc_info, **kwargs)

    def set_level(self, level: int) -> None:
        """
        Set logging level.

        Args:
            level: Logging level
        """
        self._logger.setLevel(level)


# Global logger instance
logger = Logger()

# Backward compatibility
logging = logger.get_logger()
