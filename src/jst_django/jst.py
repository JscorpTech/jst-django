import questionary.question
import os
from rich import print
import typer
from cookiecutter.main import cookiecutter
import questionary
from typing import Annotated
from .generate import Generate
from .utils import Jst
from .api import Github
from .translate import Translate
from .module import Module
from jst_aicommit.main import JstAiCommit

app = typer.Typer()

BASE_DIR = os.getcwd()


@app.command(name="install", help="Modul o'rnatish")
def install_module(
    module_name: Annotated[str, typer.Argument()] = None, version: str = typer.Option(None, "--version", "-v")
):
    Module().run(module_name, version)


@app.command(name="create", help="Yangi loyiha yaratish")
def create_project(version: str = typer.Option(None, "--version", "-v")):
    if version is None:
        version = Github().latest_release()
        print("version: ", version)
    else:
        Github().releases(version)
    template = questionary.text("Template: ", default="django").ask()
    if template == "django" or (template.startswith("http") is not True and not os.path.exists(template)):
        template = "https://github.com/JscorpTech/{}".format(template)
    choices = [
        "cacheops",
        "silk",
        "storage",
        "rosetta",
        "channels",
        "ckeditor",
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
    answers["project_slug"] = answers["project_name"].lower().replace(" ", "_").replace("-", "_").replace(".", "_")
    packages = answers.pop("packages")
    context = {
        **{choice: choice in packages for choice in choices},
        **answers,
    }
    cookiecutter(
        template,
        checkout=version,
        no_input=True,
        extra_context=context,
    )


@app.command(name="generate", help="Compoment generatsiya qilish")
def generate():
    Generate().run()


@app.command(name="aic", help="O'zgarishlarga qarab atomatik git commit yaratadi")
def aic():
    JstAiCommit().run()


@app.command(name="init", help="jst.json config faylini yaratish")
def init():
    Jst().make_config()


@app.command(name="requirements", help="Kerakli kutubxonalar")
def requirements():
    Jst().requirements()


@app.command(name="translate", help="Avtomatik tarjima")
def translate():
    Translate().run()


if __name__ == "__main__":
    app()
