import os
from rich import print
import json
from typing import Union
from pathlib import Path


class Jst:

    def __init__(self):
        self.base_dir = os.getcwd()
        self.config = {
            "dirs": {
                "apps": "./",
                "locale": "./locale/",
            },
            "stubs": {},
        }

    def _check_config(self) -> Union[bool]:
        """Config fayil mavjudligini tekshirish"""
        return os.path.exists(os.path.join(os.getcwd(), "jst.json"))

    def make_config(self):
        """Config fayil yaratish"""
        if self._check_config():
            print("[bold red]config fayli mavjud.[/bold red]")
            exit()
        with open("jst.json", "w") as file:
            json.dump(self.config, file, indent=4)
        print("[bold green]config yaratildi.[/bold green]")

    def load_config(self):
        """Config fayilni o'qish"""
        if not self._check_config():
            print("[bold red]config fayli topilmadi iltimos jst init commandasidan foydalaning.[/bold red]")
            exit()
        with open("jst.json", "r") as file:
            return json.load(file)

    def requirements(self):
        requirements = Path(os.path.dirname(__file__)).parent.joinpath("stubs", "requirements.txt.stub")
        with open(requirements, "r") as file:
            print(file.read())
