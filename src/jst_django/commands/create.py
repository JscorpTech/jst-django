"""Project creation command."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import questionary
import typer
from cookiecutter.main import cookiecutter
from rich import print

from jst_django.cli.app import app
from jst_django.constants import (
    AVAILABLE_PACKAGES,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_PHONE,
    DEFAULT_DJANGO_KEY,
    DEFAULT_LINE_LENGTH,
    DEFAULT_PORT,
    RUNNER_TYPES,
    SCRIPT_FILES,
    SETTINGS_MODULES,
    SUCCESS_PROJECT_CREATED,
)
from jst_django.exceptions import APIError, ValidationError, VersionError
from jst_django.utils import cancel, get_progress
from jst_django.utils.api import Github
from jst_django.utils.logger import logger
from jst_django.validators import Validator


class ProjectCreator:
    """Handle project creation operations."""

    def __init__(self, version: Optional[str] = None):
        """
        Initialize project creator.

        Args:
            version: Template version to use
        """
        self.version = version
        self.template_url = "https://github.com/JscorpTech/django"
        self.github = Github()
        self.validator = Validator()

    def fetch_version(self) -> str:
        """
        Fetch and validate template version.

        Returns:
            Version string

        Raises:
            APIError: If version fetch fails
            VersionError: If version is invalid
        """
        try:
            if self.version is None:
                logger.info("Fetching latest version from GitHub")
                self.version = self.github.latest_release()
                print(f"[green]Using latest version: {self.version}[/green]")
            else:
                logger.info(f"Validating version: {self.version}")
                self.github.releases(self.version)

            return self.version

        except (APIError, VersionError) as e:
            logger.error(f"Version validation failed: {e}")
            raise

    def collect_user_input(self) -> Dict[str, any]:
        """
        Collect user input through interactive prompts.

        Returns:
            Dictionary of user answers

        Raises:
            ValidationError: If validation fails
        """
        questions = {
            "project_name": {
                "type": "text",
                "message": "Project name:",
                "validate": lambda x: self.validator.validate_project_name(x),
            },
            "settings_module": {
                "type": "select",
                "message": "Settings file",
                "choices": SETTINGS_MODULES,
            },
            "packages": {
                "type": "checkbox",
                "message": "O'rtailadigan kutubxonalarni tanlang",
                "choices": AVAILABLE_PACKAGES,
            },
            "runner": {
                "type": "select",
                "message": "Runner",
                "choices": RUNNER_TYPES,
            },
            "script": {
                "type": "select",
                "message": "Script file",
                "choices": SCRIPT_FILES,
            },
            "key": {
                "type": "text",
                "default": DEFAULT_DJANGO_KEY,
                "message": "Django key (change in production!):",
            },
            "port": {
                "type": "text",
                "default": DEFAULT_PORT,
                "message": "Port:",
                "validate": lambda x: self.validator.validate_port(x),
            },
            "phone": {
                "type": "text",
                "default": DEFAULT_ADMIN_PHONE,
                "message": "Default admin phone:",
                "validate": lambda x: self.validator.validate_phone_number(x),
            },
            "password": {
                "type": "password",
                "default": DEFAULT_ADMIN_PASSWORD,
                "message": "Admin password:",
                "validate": lambda x: self.validator.validate_password_strength(x),
            },
            "max_line_length": {
                "type": "text",
                "default": str(DEFAULT_LINE_LENGTH),
                "message": "Flake8 and black max line length:",
            },
        }

        answers = {}
        logger.info("Collecting user input")

        for key, config in questions.items():
            method = config.pop("type")
            try:
                answer = getattr(questionary, method)(**config).ask()

                if answer is None:
                    logger.warning("User cancelled operation")
                    cancel()

                answers[key] = answer
                logger.debug(f"Collected {key}: {answer if key != 'password' else '***'}")

            except ValidationError as e:
                logger.error(f"Validation failed for {key}: {e}")
                print(f"[red]Error: {e}[/red]")
                raise

        return answers

    def prepare_context(self, answers: Dict[str, any]) -> Dict[str, any]:
        """
        Prepare cookiecutter context from user answers.

        Args:
            answers: User answers dictionary

        Returns:
            Context dictionary for cookiecutter
        """
        logger.info("Preparing project context")

        # Generate project slug
        project_name = answers["project_name"]
        project_slug = project_name.lower().replace(" ", "_").replace("-", "_").replace(".", "_")
        answers["project_slug"] = project_slug

        # Extract packages
        packages = answers.pop("packages")

        # Build context
        context = {
            **{choice: choice in packages for choice in AVAILABLE_PACKAGES},
            **answers,
        }

        logger.debug(f"Project slug: {project_slug}")
        logger.debug(f"Selected packages: {packages}")

        return context

    def create_project(self, context: Dict[str, any]) -> None:
        """
        Create project using cookiecutter.

        Args:
            context: Project context

        Raises:
            Exception: If project creation fails
        """
        project_slug = context["project_slug"]

        try:
            logger.info(f"Creating project: {project_slug}")

            with get_progress() as progress:
                task1 = progress.add_task("[magenta]Creating project structure")
                task2 = progress.add_task("[magenta]Creating cruft config")

                # Create project with cookiecutter
                cookiecutter(
                    self.template_url,
                    checkout=self.version,
                    no_input=True,
                    extra_context=context,
                )
                progress.update(task1, description="[green]√ Project structure created")

                # Create cruft config
                cruft_config = {
                    "template": self.template_url,
                    "commit": self.github.get_commit_id(self.version),
                    "checkout": None,
                    "context": {"cookiecutter": context},
                    "directory": None,
                }

                cruft_config_path = Path(project_slug) / ".cruft.json"
                with open(cruft_config_path, "w", encoding="utf-8") as file:
                    json.dump(cruft_config, file, indent=2, ensure_ascii=False)

                progress.update(task2, description="[green]√ Cruft config created")

            logger.info(SUCCESS_PROJECT_CREATED)
            print(f"\n[bold green]{SUCCESS_PROJECT_CREATED}[/bold green]")
            print(f"[cyan]Project location: {Path(project_slug).absolute()}[/cyan]")

        except Exception as e:
            logger.exception("Project creation failed")
            print(f"[red]Error creating project: {e}[/red]")
            raise

    def run(self) -> None:
        """Run the complete project creation flow."""
        try:
            # Fetch and validate version
            with get_progress() as progress:
                task = progress.add_task("[cyan]Fetching version")
                self.fetch_version()
                progress.update(task, description="[green]√ Version fetched")

            # Collect user input
            answers = self.collect_user_input()

            # Prepare context
            context = self.prepare_context(answers)

            # Create project
            self.create_project(context)

        except (APIError, VersionError, ValidationError) as e:
            logger.error(f"Project creation failed: {e}")
            print(f"[red]Error: {e}[/red]")
            if e.details:
                print(f"[yellow]{e.details}[/yellow]")
            raise typer.Exit(code=1)

        except Exception as e:
            logger.exception("Unexpected error during project creation")
            print(f"[red]Unexpected error: {e}[/red]")
            raise typer.Exit(code=1)


@app.command(name="create", help="Yangi loyiha yaratish")
def create_project(version: Optional[str] = typer.Option(None, "--version", "-v", help="Template version")):
    """
    Create a new Django project.

    Args:
        version: Template version to use (default: latest)
    """
    creator = ProjectCreator(version=version)
    creator.run()
