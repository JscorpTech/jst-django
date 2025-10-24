"""Global constants for jst-django project."""

# Default values
DEFAULT_PORT = "8081"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_PHONE = "998000000000"
DEFAULT_LINE_LENGTH = 120
DEFAULT_DJANGO_KEY = "django-insecure-change-this-in-production"

# File extensions
PYTHON_EXTENSION = ".py"
STUB_EXTENSION = ".stub"

# Module types
MODULES = [
    "model",
    "serializer",
    "view",
    "permission",
    "admin",
    "test",
    "translation",
    "validator",
    "form",
    "filter",
    "signal",
]

# Stub mappings
STUB_FILES = {
    "init": "__init__.stub",
    "model": "model.stub",
    "serializer": "serializer.stub",
    "view": "view.stub",
    "permission": "permission.stub",
    "admin": "admin.stub",
    "test": "test.stub",
    "translation": "translation.stub",
    "validator": "validator.stub",
    "form": "form.stub",
    "filter": "filter.stub",
    "signal": "signal.stub",
}

# Template choices
TEMPLATE_TYPES = ["django"]

# Package choices for installation
AVAILABLE_PACKAGES = [
    "cacheops",
    "silk",
    "storage",
    "channels",
    "ckeditor",
    "modeltranslation",
    "parler",
    "rosetta",
]

# Runner types
RUNNER_TYPES = ["wsgi", "asgi"]

# Script files
SCRIPT_FILES = ["entrypoint.sh", "entrypoint-server.sh"]

# Settings modules
SETTINGS_MODULES = [
    "config.settings.local",
    "config.settings.production",
]

# Validation patterns
PROJECT_NAME_PATTERN = r"^(?=.*[A-Za-z])[A-Za-z0-9]+$"
PHONE_PATTERN = r"^\d{10,15}$"

# Paths
DEFAULT_APPS_PATH = "./core/apps/"
DEFAULT_MODELS_PATH = "models/"
DEFAULT_SERIALIZERS_PATH = "serializers/"
DEFAULT_VIEWS_PATH = "views/"
DEFAULT_PERMISSIONS_PATH = "permissions/"
DEFAULT_ADMIN_PATH = "admin/"
DEFAULT_TESTS_PATH = "tests/"
DEFAULT_TRANSLATION_PATH = "translation/"
DEFAULT_VALIDATORS_PATH = "validators/"
DEFAULT_FORMS_PATH = "forms/"
DEFAULT_FILTERS_PATH = "filters/"
DEFAULT_SIGNALS_PATH = "signals/"

# Import path
DEFAULT_IMPORT_PATH = "core.apps."

# Error messages
ERROR_INVALID_PROJECT_NAME = "Project name must contain at least one letter and only alphanumeric characters"
ERROR_INVALID_PHONE = "Phone number must be 10-15 digits"
ERROR_MODULE_NOT_FOUND = "Module '{}' not found"
ERROR_APP_NOT_FOUND = "App '{}' not found"
ERROR_STUB_NOT_FOUND = "Stub file '{}' does not exist"
ERROR_EMPTY_NAME = "Name cannot be empty"
ERROR_INVALID_PATH = "Invalid path format. Expected: app_name/file_name/model_name"

# Success messages
SUCCESS_PROJECT_CREATED = "Project created successfully"
SUCCESS_APP_CREATED = "App '{}' created successfully"
SUCCESS_MODULE_GENERATED = "Module '{}' generated successfully"
SUCCESS_FILES_FORMATTED = "Files formatted successfully"
