.PHONY: help install install-dev test lint format type-check clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	poetry install --no-dev

install-dev: ## Install all dependencies including dev
	poetry install
	pip install -r requirements-dev.txt

test: ## Run tests with coverage
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/ -v -m unit

test-integration: ## Run integration tests only
	pytest tests/ -v -m integration

lint: ## Run linters
	flake8 src/jst_django
	black --check src/jst_django tests
	isort --check-only src/jst_django tests

format: ## Format code with black and isort
	black src/jst_django tests
	isort src/jst_django tests

type-check: ## Run type checking with mypy
	mypy src/jst_django --ignore-missing-imports

check: lint type-check test ## Run all checks (lint, type-check, test)

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

build: clean ## Build distribution packages
	poetry build

publish: build ## Publish to PyPI
	poetry publish

publish-test: build ## Publish to Test PyPI
	poetry publish --repository testpypi

version: ## Show current version
	@poetry version

bump-patch: ## Bump patch version (0.0.X)
	poetry version patch

bump-minor: ## Bump minor version (0.X.0)
	poetry version minor

bump-major: ## Bump major version (X.0.0)
	poetry version major

pre-commit: ## Install pre-commit hooks
	pre-commit install

run-hooks: ## Run pre-commit hooks on all files
	pre-commit run --all-files

coverage-html: ## Generate HTML coverage report
	pytest tests/ --cov=src/jst_django --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

coverage-xml: ## Generate XML coverage report
	pytest tests/ --cov=src/jst_django --cov-report=xml

dev: install-dev ## Setup development environment
	@echo "Development environment setup complete!"

ci: lint type-check test ## Run CI checks
	@echo "CI checks passed!"
