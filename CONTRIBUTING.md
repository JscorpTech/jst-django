# Contributing to JST-Django

Thank you for your interest in contributing to JST-Django! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/JscorpTech/jst-django.git
cd jst-django
```

2. **Install Poetry** (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies**
```bash
make install-dev
```

4. **Install pre-commit hooks**
```bash
make pre-commit
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, documented code
- Follow the code style guidelines
- Add tests for new features
- Update documentation as needed

### 3. Run Tests
```bash
make test
```

### 4. Run Linters
```bash
make lint
```

### 5. Format Code
```bash
make format
```

### 6. Run All Checks
```bash
make check
```

## Code Style Guidelines

### Python Code Style
- **PEP 8**: Follow PEP 8 guidelines
- **Line Length**: Maximum 120 characters
- **Imports**: Use isort for import ordering
- **Formatting**: Use black for code formatting
- **Type Hints**: Add type hints to all functions
- **Docstrings**: Document all public functions and classes

### Example Function
```python
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
        raise ValidationError("Name cannot be empty")
    return True
```

### Docstring Format
We use Google-style docstrings:
```python
def function(arg1: str, arg2: int) -> bool:
    """
    Short description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

## Testing Guidelines

### Writing Tests
- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use pytest fixtures for common setup
- Mock external dependencies

### Test Structure
```python
import pytest
from jst_django.validators import Validator

class TestValidator:
    """Test Validator class."""

    def test_validate_project_name_valid(self):
        """Test valid project name."""
        assert Validator.validate_project_name("MyProject") is True

    def test_validate_project_name_invalid(self):
        """Test invalid project name."""
        with pytest.raises(ValidationError):
            Validator.validate_project_name("")
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_validators.py -v

# Run tests with coverage
make coverage-html
```

## Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```
feat(validators): add phone number validation

Add validation for phone numbers with configurable pattern.
Supports international formats.

Closes #123
```

```
fix(api): handle API timeout errors

Add proper error handling for GitHub API timeouts.
Set default timeout to 30 seconds.
```

## Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Update ARCHITECTURE.md for structural changes
   - Add docstrings to new functions

2. **Add Tests**
   - Add unit tests for new functionality
   - Ensure test coverage doesn't decrease
   - All tests must pass

3. **Run Checks**
   ```bash
   make check
   ```

4. **Create Pull Request**
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

5. **Address Review Comments**
   - Make requested changes
   - Push updates to the same branch
   - Re-request review when ready

## Issue Reporting

### Bug Reports
Include:
- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/tracebacks

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## Code Review Checklist

Before submitting for review, ensure:

- [ ] Code follows style guidelines
- [ ] Tests are added and passing
- [ ] Documentation is updated
- [ ] Commits follow commit message format
- [ ] All CI checks pass
- [ ] No merge conflicts
- [ ] Changes are focused and atomic

## Questions?

- Open an issue for questions
- Join our community discussions
- Check existing documentation

Thank you for contributing to JST-Django! 🎉
