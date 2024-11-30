import questionary.question
import os
from rich import print
import typer
from cookiecutter.main import cookiecutter
import questionary
from typing import Annotated
from .generate import Generate
from .api import Github
from .translate import Translate
from .module import Module
from jst_aicommit.main import JstAiCommit

app = typer.Typer()

BASE_DIR = os.getcwd()


def error(data):
    print(f"[bold red]{data}[/bold red]")


def success(data):
    print(f"[bold green]{data}[/bold green]")


def info(data):
    print(f"[bold blue]{data}[/bold blue]")


@app.command(name="install", help="Modul o'rnatish")
def install_module(
    module_name: Annotated[str, typer.Argument()] = None,
    version: str = typer.Option(None, "--version", "-v")
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
    if template.startswith("http") is not True:
        template = "https://github.com/JscorpTech/{}".format(template)
    cookiecutter(template, checkout=version)


@app.command(name="generate", help="Compoment generatsiya qilish")
def generate():
    Generate().run()


@app.command(name="aic", help="O'zgarishlarga qarab atomatik git commit yaratadi")
def aic():
    JstAiCommit().run()


@app.command(name="translate", help="Avtomatik tarjima")
def translate():
    Translate().run()


if __name__ == "__main__":
    app()
