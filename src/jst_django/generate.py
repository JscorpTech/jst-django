from typing import List, Optional, Generator, Dict, Any, LiteralString
import os
import questionary
from .utils import File, Code, Jst, cancel
from pathlib import Path
from os.path import join


def directory_ls(path: str) -> Generator[Path, None, None]:
    """Directory items list"""
    ignore = ["logs"]
    for item in Path(path).iterdir():
        if item.name not in ignore and item.is_dir():
            yield item


def get_file_name(module: str, name: str, extension: bool = True) -> str:
    """Get file name"""
    extension = ".py" if extension else ""
    return f"test_{name}{extension}" if module == "test" else f"{name}{extension}"


class Generate:
    name: Optional[str] = None
    file_name: Optional[str] = None
    modules: List[str]
    stubs: Dict[str, str]

    def __init__(self) -> None:
        self.config = Jst().load_config()
        dirs = self.config.get("dirs", {})
        self.path = {
            "apps": dirs.get("apps", "./core/apps/"),
            "model": dirs.get("models", "models/"),
            "serializer": dirs.get("serializers", "serializers/"),
            "view": dirs.get("views", "views/"),
            "permission": dirs.get("permissions", "permissions/"),
            "admin": dirs.get("admin", "admin/"),
            "test": dirs.get("tests", "tests/"),
            "translation": dirs.get("translation", "translation/"),
            "validator": dirs.get("validators", "validators/"),
            "form": dirs.get("forms", "forms/"),
            "filter": dirs.get("filters", "filters/"),
            "signal": dirs.get("signals", "signals/"),
            "stubs": join(os.path.dirname(__file__), "stubs"),
        }
        self.modules = [
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
        self.stubs = {
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
        } | self.config.get("stubs", {})

    def _get_apps(self) -> Generator[str, None, None]:
        """Return list of Django apps"""
        dirs = directory_ls(self.path["apps"])
        for item in dirs:
            if item.joinpath("apps.py").exists():
                yield item.name

    def __get_stub_path(self, name: str) -> Path:
        """Get stub file path"""
        if Path(self.stubs[name]).exists():
            return Path(self.stubs[name])
        path = Path(self.path["stubs"], self.stubs[name])
        if path.exists():
            return path
        raise FileNotFoundError("Stub file does not exist")

    def _read_stub(self, name: str, append: bool = False) -> tuple[str | Any, LiteralString | str | Any]:
        """Get stub content"""
        response = ""
        top_content = ""
        with open(self.__get_stub_path(name)) as file:
            for chunk in file.readlines():
                if chunk.startswith("!!"):
                    top_content += chunk.replace("!!", "", 2)
                    continue
                elif append and chunk.startswith("##"):
                    continue
                elif not append and chunk.startswith("##"):
                    chunk = chunk.replace("##", "", 2)
                response += chunk
        if append:
            response = "\n" + response
        return top_content, response

    def _get_module_name(self, prefix: str = "") -> str:
        return f"{self.name.capitalize()}{prefix}"

    def _write_file(
        self,
        file_path: str,
        stub: str,
        prefix: str = "",
        append: bool = False,
    ):
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        with open(file_path, "r+") as file:
            file_content = file.read()
            top_content, content = self._read_stub(stub, append=append)
            file.seek(0)
            file.write(top_content % {"name_cap": self.name.capitalize(), "file_name": self.file_name})
            file.write(file_content)
            file.write(
                content
                % {
                    "class_name": self._get_module_name(prefix),
                    "name": self.name,
                    "name_cap": self.name.capitalize(),
                }
            )

    def _import_init(self, init_path: str, file_name: str):
        """Import necessary files into __init__.py, create if not exists"""
        with open(init_path, "a") as file:
            file.write(self._read_stub("init")[1] % {"file_name": file_name})
        Code.format_code(init_path)

    def _generate_files(self, app: str, modules: List[str]) -> bool:
        """Create necessary folders if not found"""
        apps_dir = join(self.path["apps"], app)
        for module in modules:
            module_dir = join(apps_dir, self.path[module])
            file_path = join(module_dir, get_file_name(module, self.file_name))
            init_path = join(module_dir, "__init__.py")
            File.mkdir(module_dir)
            if module == "serializer":
                module_dir = join(module_dir, self.file_name)
                file_path = join(module_dir, f"{self.name}.py")
                File.mkdir(module_dir)
                self._import_init(join(module_dir, "__init__.py"), file_name=self.name)
            if not os.path.exists(file_path):
                self._import_init(init_path, get_file_name(module, self.file_name, extension=False))
                self._write_file(file_path, module, module.capitalize())
            else:
                self._write_file(file_path, module, module.capitalize(), append=True)
            Code.format_code(file_path)
        return True

    def run(self) -> None:
        """Run the generator"""
        self.file_name = questionary.text("File Name: ", validate=lambda x: True if len(x) > 0 else False).ask()
        if self.file_name is None:
            return cancel()
        names = questionary.text("Name: ", multiline=True, validate=lambda x: True if len(x) > 0 else False).ask()
        if names is None:
            return cancel()
        names = names.split("\n")
        if len(names) == 0:
            raise Exception("Name can not be empty")
        app = questionary.select("Select App", choices=list(self._get_apps())).ask()
        if app is None:
            return cancel()
        modules = questionary.checkbox("Select required modules", self.modules).ask()
        if modules is None:
            return cancel()
        for name in names:
            if len(name) == 0:
                continue
            self.name = name
            self._generate_files(app, modules)
