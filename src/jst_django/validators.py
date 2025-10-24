"""Input validation utilities."""

import re
from pathlib import Path
from typing import Optional

from jst_django.constants import (ERROR_EMPTY_NAME, ERROR_INVALID_PATH,
                                  ERROR_INVALID_PHONE,
                                  ERROR_INVALID_PROJECT_NAME, PHONE_PATTERN,
                                  PROJECT_NAME_PATTERN)
from jst_django.exceptions import ValidationError


class Validator:
    """Base validator class."""

    @staticmethod
    def validate_project_name(name: str) -> bool:
        """
        Validate project name.

        Args:
            name: Project name to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not name or len(name.strip()) == 0:
            raise ValidationError(ERROR_EMPTY_NAME)

        if not re.match(PROJECT_NAME_PATTERN, name):
            raise ValidationError(ERROR_INVALID_PROJECT_NAME)

        return True

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not phone or len(phone.strip()) == 0:
            raise ValidationError(ERROR_EMPTY_NAME)

        if not re.match(PHONE_PATTERN, phone):
            raise ValidationError(ERROR_INVALID_PHONE)

        return True

    @staticmethod
    def validate_module_path(path: str, min_parts: int = 3) -> tuple[str, ...]:
        """
        Validate and parse module path.

        Args:
            path: Module path in format app_name/file_name/model_name
            min_parts: Minimum number of path parts required

        Returns:
            Tuple of path parts

        Raises:
            ValidationError: If validation fails
        """
        if not path or len(path.strip()) == 0:
            raise ValidationError(ERROR_EMPTY_NAME)

        parts = path.split("/")
        if len(parts) < min_parts:
            raise ValidationError(ERROR_INVALID_PATH)

        return tuple(parts)

    @staticmethod
    def validate_path_exists(path: Path, must_exist: bool = True) -> bool:
        """
        Validate if path exists.

        Args:
            path: Path to validate
            must_exist: Whether path must exist

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if must_exist and not path.exists():
            raise ValidationError(f"Path does not exist: {path}")

        if not must_exist and path.exists():
            raise ValidationError(f"Path already exists: {path}")

        return True

    @staticmethod
    def validate_not_empty(value: str, field_name: str = "Value") -> bool:
        """
        Validate that value is not empty.

        Args:
            value: Value to validate
            field_name: Name of the field for error message

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not value or len(value.strip()) == 0:
            raise ValidationError(f"{field_name} cannot be empty")

        return True

    @staticmethod
    def validate_list_not_empty(items: list, field_name: str = "List") -> bool:
        """
        Validate that list is not empty.

        Args:
            items: List to validate
            field_name: Name of the field for error message

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not items or len(items) == 0:
            raise ValidationError(f"{field_name} cannot be empty")

        return True

    @staticmethod
    def validate_password_strength(password: str, min_length: int = 8) -> bool:
        """
        Validate password strength.

        Args:
            password: Password to validate
            min_length: Minimum password length

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not password or len(password) < min_length:
            raise ValidationError(f"Password must be at least {min_length} characters long")

        return True

    @staticmethod
    def validate_port(port: str) -> bool:
        """
        Validate port number.

        Args:
            port: Port to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValidationError("Port must be between 1 and 65535")
        except ValueError:
            raise ValidationError("Port must be a valid number")

        return True
