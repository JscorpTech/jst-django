"""Custom exceptions for jst-django."""


class JstDjangoException(Exception):
    """Base exception for all jst-django errors."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ValidationError(JstDjangoException):
    """Raised when input validation fails."""

    pass


class FileOperationError(JstDjangoException):
    """Raised when file operations fail."""

    pass


class StubNotFoundError(JstDjangoException):
    """Raised when stub file is not found."""

    pass


class AppNotFoundError(JstDjangoException):
    """Raised when Django app is not found."""

    pass


class ModuleNotFoundError(JstDjangoException):
    """Raised when module is not found."""

    pass


class ConfigurationError(JstDjangoException):
    """Raised when configuration is invalid or missing."""

    pass


class TemplateError(JstDjangoException):
    """Raised when template rendering fails."""

    pass


class CodeGenerationError(JstDjangoException):
    """Raised when code generation fails."""

    pass


class APIError(JstDjangoException):
    """Raised when API calls fail."""

    pass


class VersionError(JstDjangoException):
    """Raised when version-related operations fail."""

    pass
