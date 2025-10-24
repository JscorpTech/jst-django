import os
from os.path import join
from pathlib import Path
from typing import Annotated, Any, Dict, Generator, List, Literal, LiteralString, Optional

import jinja2
import questionary
import typer

from jst_django.cli.app import app
from jst_django.commands.install import Module
from jst_django.utils import Code, File, Jst, cancel
from jst_django.utils.ast_utils import add_include_urlpattern, add_module, add_router_registration_with_import
from jst_django.utils.code import format_code_string
from jst_django.utils.tokenize import Tokenize

MODULES = List[
    Literal[
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
]

FIELDS = typer.Option(
    default="name:str", confirmation_prompt=True, help="name:type names[char,int,text,date,time,datetime,image,bool]"
)


class Generate:
    modules: List[str]
    stubs: Dict[str, str]

    def __init__(self) -> None:
        self.name: str = ""
        self.file_name: str = ""
        self.sub_folder: Optional[str] = None
        self.selected_modules: Optional[list] = None
        self.app = None
        self.module = None
        self.fields: Tokenize

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
            "stubs": join(os.path.dirname(__file__), "../stubs"),
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

    def _upper(self, text: str) -> str:
        return text[0].upper() + text[1:]

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
        raise FileNotFoundError(f"Stub file does not exist {name}")

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

    def _get_module_path(self, module: str) -> str:
        path = self.path[module]
        if self.sub_folder is not None:
            path = f"{path}{self.sub_folder}"
        return path

    def _get_import_path(self, path: str, sub: bool = False) -> str:
        import_sub_path = "." + self.sub_folder.replace("/", ".") if self.sub_folder is not None else ""
        import_path = self.config.get("import_path", "core.apps.")
        if sub is True:
            import_sub_path += f".{self.file_name}"
        return f"{import_path}{self.app}.{path}{import_sub_path}"

    def _write_file(
        self,
        file_path: str,
        stub: str,
        prefix: str = "",
        append: bool = False,
    ):
        import_path = {
            "model_import_path": self._get_import_path("models"),
            "serializer_import_path": self._get_import_path("serializers", True),
        }
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        with open(file_path, "r+") as file:
            file_content = file.read()
            top_content, content = self._read_stub(stub, append=append)
            file.seek(0)
            file.write(
                jinja2.Template(top_content + "\n").render(
                    **{"name_cap": self.name.capitalize(), "file_name": self.file_name, **import_path}
                )
            )
            file.write(file_content)
            file.write(
                jinja2.Template(content).render(
                    **{
                        "class_name": self._get_module_name(prefix),
                        "name": self.name,
                        "name_cap": self.name.capitalize(),
                        "file_name": self.file_name,
                        "model_fields": self.fields.model,
                        "fields": self.fields.keys,
                        **import_path,
                    }
                )
            )

    def _import_init(self, init_path: str, file_name: str):
        """Import necessary files into __init__.py, create if not exists"""
        with open(init_path, "a") as file:
            file.write(jinja2.Template(self._read_stub("init")[1]).render(file_name=file_name))
        Code.format_code(init_path)

    def _generate_files(self, app: str, modules: MODULES) -> bool:
        """Create necessary folders if not found"""
        apps_dir = join(self.path["apps"], app)
        for module in modules:
            module_dir = join(apps_dir, self._get_module_path(module))
            self.module = module
            Path(module_dir).mkdir(parents=True, exist_ok=True)
            file_path = join(module_dir, get_file_name(module, self.file_name))
            init_path = join(module_dir, "__init__.py")
            if module in ["serializer", "test"]:
                module_dir = join(module_dir, self.file_name)
                file_path = join(module_dir, get_file_name(module, self.name))
                File.mkdir(module_dir)
                self._import_init(
                    join(module_dir, "__init__.py"),
                    file_name=get_file_name(module, self.name, _extension=False),
                )
            if not os.path.exists(file_path):
                self._import_init(init_path, self.file_name)
                self._write_file(file_path, module, module.capitalize())
            else:
                self._write_file(file_path, module, module.capitalize(), append=True)
            Code.format_code(file_path)
        return True

    def make_module(self, module_path: str, modules: MODULES) -> None:
        parts = module_path.split("/")
        if not len(parts) >= 3:
            raise Exception("Model manzili to'g'ri kiritilmadi example: app_name.file_name.model_name")
        app_name = parts[0]
        self.app = app_name
        path_parts = parts[1:-1]
        name = path_parts.pop()
        model_name = parts[-1]
        path = "/".join(path_parts)
        Path(path).mkdir(parents=True, exist_ok=True)
        generate = Generate()
        generate.sub_folder = path if len(path_parts) > 1 else None
        generate.file_name = name
        generate.name = model_name
        generate._generate_files(app_name, modules)

    def auto_generate(self, file_name: str) -> None:
        """Run the generator"""
        self.file_name = file_name
        filename_parts = self.file_name.split("/")
        if len(filename_parts) > 1:
            self.file_name = filename_parts[-1]
        self.sub_folder = "/".join(filename_parts[:-1]) if len(filename_parts) > 1 else None
        names = questionary.text("Name: ", multiline=True, validate=lambda x: True if len(x) > 0 else False).ask()
        if names is None:
            return cancel()
        names = names.split("\n")
        if len(names) == 0:
            raise Exception("Name can not be empty")
        app = questionary.select("Select App", choices=list(self._get_apps())).ask()
        if app is None:
            return cancel()
        self.app = app
        if self.selected_modules is None:
            modules = questionary.checkbox("Select required modules", choices=self.modules).ask()
        else:
            modules = self.selected_modules
        if modules is None:
            return cancel()
        for name in names:
            if len(name) == 0:
                continue
            self.name = name
            self._generate_files(app, modules)
            with open(self.path.get("apps") + app + "/urls.py", "r+") as file:
                result = add_router_registration_with_import(file.read(), self._upper(name) + "View", name)
                file.seek(0)
                file.truncate()
                code = format_code_string(result)
                if code is not None:
                    file.write(code)


def directory_ls(path: str) -> Generator[Path, None, None]:
    """Directory items list"""
    ignore = ["logs"]
    for item in Path(path).iterdir():
        if item.name not in ignore and item.is_dir():
            yield item


def get_file_name(module: str, name: str, _extension: bool = True) -> str:
    """Get file name"""
    extension = ".py" if _extension else ""
    return f"test_{name}{extension}" if module == "test" else f"{name}{extension}"


@app.command(name="make:module", help="Compoment generatsiya qilish")
def generate_module(module_name: Annotated[str, typer.Argument()], fields: str = FIELDS):
    generate = Generate()
    tokenize = Tokenize(fields.strip())
    generate.selected_modules = None
    generate.fields = tokenize.make()
    generate.auto_generate(module_name)


@app.command(name="make:app", help="Modul o'rnatish")
def generate_app(module_name: Annotated[str, typer.Argument()], version: str = typer.Option(None, "--version", "-v")):
    if module_name is None:
        raise Exception("Module name is required")

    result = Module().run(module_name, version)
    if result:
        with open("config/conf/modules.py", "r+") as file:
            code = format_code_string(add_module(file.read(), "core.apps.%s" % module_name))
            if code is not None:
                file.seek(0)
                file.truncate()
                file.write(code)
        with open("config/urls.py", "r+") as file:
            code = format_code_string(add_include_urlpattern(file.read(), "api/", "core.apps.%s.urls" % module_name))
            if code is not None:
                file.seek(0)
                file.truncate()
                file.write(code)


@app.command(name="make:crud", help="CRUD generatsiya qilish")
def generate_crud(module_name: Annotated[str, typer.Argument()], fields: str = FIELDS):
    generate = Generate()
    tokenize = Tokenize(fields.strip())
    generate.selected_modules = generate.modules
    generate.fields = tokenize.make()
    generate.auto_generate(module_name)


@app.command(name="make:model", help="generate model")
def make_model(model_path: str = typer.Argument(..., help="Model path")):
    generate = Generate()
    generate.make_module(model_path, ["model"])
