import typer
import os
from rich import print
from cookiecutter.main import cookiecutter
import questionary
from jst_django.utils import get_progress, cancel
from jst_django.utils.api import Github
import json
from jst_django.cli.app import app


@app.command(name="create", help="Yangi loyiha yaratish")
def create_project(version: str = typer.Option(None, "--version", "-v")):
    with get_progress() as progress:
        task1 = progress.add_task("[cyan]Fetch version")
        if version is None:
            version = Github().latest_release()
            print("version: ", version)
        else:
            Github().releases(version)
        progress.update(task1, description="[green]√ Done: Fetch version")
    template = questionary.text("Template: ", default="django").ask()
    if template is None:
        return cancel()
    if template == "django" or (template.startswith("http") is not True and not os.path.exists(template)):
        template = "https://github.com/JscorpTech/{}".format(template)
    choices = [
        "cacheops",
        "silk",
        "storage",
        "rosetta",
        "channels",
        "ckeditor",
        "modeltranslation",
        "parler",
    ]
    questions = {
        "project_name": {"type": "text", "message": "Project name: ", "default": "django"},
        "settings_module": {
            "type": "select",
            "message": "Settings file",
            "choices": [
                "config.settings.local",
                "config.settings.production",
            ],
        },
        "packages": {
            "type": "checkbox",
            "message": "O'rtailadigan kutubxonalarni tanlang",
            "choices": choices,
        },
        "runner": {
            "type": "select",
            "message": "Runner",
            "choices": ["wsgi", "asgi"],
        },
        "script": {
            "type": "select",
            "message": "Script file",
            "choices": ["entrypoint.sh", "entrypoint-server.sh"],
        },
        "key": {"type": "text", "default": "key", "message": "Django key"},
        "port": {"type": "text", "default": "8081", "message": "Port"},
        "phone": {"type": "text", "default": "998888112309", "message": "Default admin phone"},
        "password": {"type": "text", "default": "2309", "message": "Admin password"},
        "max_line_length": {"type": "text", "default": "120", "message": "Flake8 and black max line length"},
    }
    answers = {}
    for key, value in questions.items():
        method = value.pop("type")
        answers[key] = getattr(questionary, method)(**value).ask()
        if answers[key] is None:
            return cancel()
    answers["project_slug"] = answers["project_name"].lower().replace(" ", "_").replace("-", "_").replace(".", "_")
    packages = answers.pop("packages")
    context = {
        **{choice: choice in packages for choice in choices},
        **answers,
    }
    cruft_config = {
        "template": template,
        "commit": Github().get_commit_id(version),
        "checkout": None,
        "context": {"cookiecutter": context},
        "directory": None,
    }
    with get_progress() as progress:
        task1 = progress.add_task("[magenta]Creating project")
        task2 = progress.add_task("[magenta]Creating cruft config")
        cookiecutter(
            template,
            checkout=version,
            no_input=True,
            extra_context=context,
        )
        progress.update(task1, description="[green]√ Done Created project")
        with open(f"{answers['project_slug']}/.cruft.json", "w") as file:
            file.write(json.dumps(cruft_config, indent=True))
        progress.update(task2, description="[green]√ Done Created cruft config")
