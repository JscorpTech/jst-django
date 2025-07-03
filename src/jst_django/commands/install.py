import zipfile
import tempfile
import requests
import os
from jst_django.utils.api import Github
import questionary
import shutil
from uuid import uuid4
from typing import Union
from jst_django.utils import Jst, get_progress, cancel
import typer
from typing import Annotated
from jst_django.cli.app import app


def subfolder_to_parent(path):
    """ichki papkadagi ko'dlarni parent papkaga ko'chirish"""
    extracted_file = os.path.join(path, os.listdir(path)[0])

    for file in os.listdir(extracted_file):
        shutil.move(os.path.join(extracted_file, file), path)
    os.rmdir(extracted_file)


def download(url, dir) -> str:
    """modulni yuklash"""
    file = os.path.join(dir, "%s.zip" % uuid4())
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(file, "wb") as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                zip_file.write(chunk)
    return file


class Module:
    modules = {
        "default": "https://github.com/JscorpTech/module-default.git",
        "authbot": "https://github.com/JscorpTech/module-authbot.git",
        "authv2": "https://github.com/JscorpTech/module-authv2.git",
        "websocket": "https://github.com/JscorpTech/module-websocket.git",
    }

    def __init__(self):
        self.config = Jst().load_config()

    def _extract(self, module_name, zip_path):
        modules_dir = os.path.join(os.getcwd(), self.config["dirs"]["apps"])
        extract_dir = os.path.join(modules_dir, module_name)
        if os.path.exists(extract_dir):
            raise Exception("Modul mavjud")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir

    def _download_and_extract_module(self, module_name, url):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the module
            zip_path = download(url, temp_dir)
            # Extract the module
            extract_dir = self._extract(module_name, zip_path)
            # Move the module to the correct location
            subfolder_to_parent(extract_dir)

            with open(os.path.join(extract_dir, "apps.py"), "r+") as file:
                data = file.read()
                file.seek(0)
                file.write(data.replace("{{module_name}}", "%s%s" % (self.config.get("apps", ""), module_name)))
                file.truncate()

    def run(self, module_name: str, version=None):
        module = questionary.select("Modulni tanlang", choices=self.modules.keys()).ask()
        if module is None:
            return cancel()
        with get_progress() as progress:
            task1 = progress.add_task("[cyan]Fetch module")
            task2 = progress.add_task("[magenta]Install module")
            api = Github("module-%s" % module)
            if module_name is None:
                module_name = module
            modules = module_name.split(",")
            if version is None:
                version = api.latest_release()
            else:
                api.releases(version)
            progress.update(task1, description="[green]√ Done Fetch module version: %s" % version)
            module = "https://github.com/JscorpTech/module-{}/archive/refs/tags/{}.zip".format(module, version)

            for module_name in modules:
                module_name = module_name.strip()
                if len(module_name) == 0:
                    continue
                progress.update(task2, description="[cyan]Installing module: %s" % module_name)
                try:
                    self._download_and_extract_module(module_name, module)
                    progress.update(task2, description="[green]I√ Done Installed module: %s" % module_name)
                except Exception as e:
                    progress.update(task2, description="[red]Installing error: %s" % str(e))


@app.command(name="make:app", help="Modul o'rnatish")
def install_module(
    module_name: Annotated[str, typer.Argument()] = None, version: str = typer.Option(None, "--version", "-v")
):
    Module().run(module_name, version)
