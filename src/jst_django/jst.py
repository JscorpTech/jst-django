import zipfile
import tempfile
import questionary.question
import requests
import os
from rich import print, progress
import typer
from cookiecutter.main import cookiecutter
import questionary
from typing import Annotated
from .generate import Generate
from .api import Gitlab


app = typer.Typer()

BASE_DIR = os.getcwd()


def error(data):
    print(f"[bold red]{data}[/bold red]")


def success(data):
    print(f"[bold green]{data}[/bold green]")


def info(data):
    print(f"[bold blue]{data}[/bold blue]")


def download_and_extract_module(module_name, url):
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "downloaded_file.zip")

        # Download the module
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(zip_path, "wb") as zip_file:
                for chunk in response.iter_content(chunk_size=8192):
                    zip_file.write(chunk)

        # Extract the module
        modules_dir = os.path.join(BASE_DIR, "core/apps/")
        extract_dir = os.path.join(modules_dir, module_name)
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        with open(os.path.join(extract_dir, "apps.py"), "r+") as file:
            data = file.read()
            file.seek(0)
            file.write(data.replace("{{module_name}}", module_name))
            file.truncate()


def get_modules():
    response = requests.get(
        "https://gitlab.com/JscorpTech/django-modules/-/raw/main/modules.json"
    )
    response.raise_for_status()
    return response.json()


@app.command(name="install", help="Modul o'rnatish")
def install_module(
    module_name: Annotated[str, typer.Argument()] = None,
):
    module = questionary.select("Modulni tanlang", choices=get_modules()).ask()
    if module_name is None:
        module_name = module
    if module.startswith("http") is not True:
        module = (
            "https://gitlab.com/JscorpTech/django-modules/-/raw/main/{}.zip".format(
                module
            )
        )

    with progress.Progress(
        progress.SpinnerColumn(),
        progress.TextColumn("[progress.description]{task.description}"),
    ) as prg:
        task = prg.add_task("Modul o'rnatish boshlandi", total=None)
        try:
            download_and_extract_module(module_name, module)
        except Exception as e:
            prg.update(task, completed=True, description=f"[bold red]{e}[/bold red]")
        else:
            prg.update(
                task,
                completed=True,
                description="[bold green]Modul o'rnatish yakunlandi: {}[/bold green]".format(
                    BASE_DIR
                ),
            )


@app.command(name="create", help="Yangi loyiha yaratish")
def create_project():
    template = questionary.text("Template: ", default="django").ask()
    if template.startswith("http") is not True:
        template = "http://gitlab.com/JscorpTech/{}".format(template)
    branch = questionary.select(
        "Qaysi versiyadan foydalanmoqchisiz: ", Gitlab().branches()
    ).ask()
    cookiecutter(template, checkout=branch)


@app.command(name="generate", help="Compoment generatsiya qilish")
def generate():
    Generate().run()


if __name__ == "__main__":
    app()
