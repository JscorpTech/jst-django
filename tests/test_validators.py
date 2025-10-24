"""Tests for validators module."""

import pytest

from jst_django.exceptions import ValidationError
from jst_django.validators import Validator


class TestValidator:
    """Test Validator class."""

    def test_validate_project_name_valid(self):
        """Test valid project name."""
        assert Validator.validate_project_name("MyProject123") is True
        assert Validator.validate_project_name("project") is True
        assert Validator.validate_project_name("Project123") is True

    def test_validate_project_name_invalid_empty(self):
        """Test empty project name."""
        with pytest.raises(ValidationError):
            Validator.validate_project_name("")

    def test_validate_project_name_invalid_special_chars(self):
        """Test project name with special characters."""
        with pytest.raises(ValidationError):
            Validator.validate_project_name("my-project")
        with pytest.raises(ValidationError):
            Validator.validate_project_name("my_project")

    def test_validate_phone_number_valid(self):
        """Test valid phone number."""
        assert Validator.validate_phone_number("998901234567") is True
        assert Validator.validate_phone_number("1234567890") is True

    def test_validate_phone_number_invalid(self):
        """Test invalid phone number."""
        with pytest.raises(ValidationError):
            Validator.validate_phone_number("123")
        with pytest.raises(ValidationError):
            Validator.validate_phone_number("abc")

    def test_validate_module_path_valid(self):
        """Test valid module path."""
        result = Validator.validate_module_path("app/file/model")
        assert result == ("app", "file", "model")

    def test_validate_module_path_invalid(self):
        """Test invalid module path."""
        with pytest.raises(ValidationError):
            Validator.validate_module_path("app")

    def test_validate_password_strength_valid(self):
        """Test valid password."""
        assert Validator.validate_password_strength("password123") is True
        assert Validator.validate_password_strength("12345678") is True

    def test_validate_password_strength_invalid(self):
        """Test weak password."""
        with pytest.raises(ValidationError):
            Validator.validate_password_strength("123")

    def test_validate_port_valid(self):
        """Test valid port."""
        assert Validator.validate_port("8000") is True
        assert Validator.validate_port("80") is True
        assert Validator.validate_port("65535") is True

    def test_validate_port_invalid(self):
        """Test invalid port."""
        with pytest.raises(ValidationError):
            Validator.validate_port("0")
        with pytest.raises(ValidationError):
            Validator.validate_port("99999")
        with pytest.raises(ValidationError):
            Validator.validate_port("abc")
