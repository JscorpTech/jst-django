from typing import List, Optional, Generator, Dict, Any, LiteralString, Literal
import os
import questionary
from jst_django.utils import File, Code, Jst, cancel
from pathlib import Path
from os.path import join
from jst_django.cli.app import app
import typer
import jinja2
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
            if module == "serializer":
                module_dir = join(module_dir, self.file_name)
                file_path = join(module_dir, f"{self.name}.py")
                File.mkdir(module_dir)
                self._import_init(join(module_dir, "__init__.py"), file_name=self.name)
            if not os.path.exists(file_path):
                self._import_init(init_path, get_file_name(module, self.file_name, _extension=False))
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

    def auto_generate(self) -> None:
        """Run the generator"""
        self.file_name = questionary.text("File Name: ", validate=lambda x: True if len(x) > 0 else False).ask()
        if self.file_name is None:
            return cancel()
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
def generate_module(fields: str = FIELDS):
    generate = Generate()
    tokenize = Tokenize(fields.strip())
    generate.selected_modules = None
    generate.fields = tokenize.make()
    generate.auto_generate()


@app.command(name="make:crud", help="CRUD generatsiya qilish")
def generate_crud(fields: str = FIELDS):
    generate = Generate()
    tokenize = Tokenize(fields.strip())
    generate.selected_modules = generate.modules
    generate.fields = tokenize.make()
    generate.auto_generate()


@app.command(name="make:model", help="generate model")
def make_model(model_path: str = typer.Argument(..., help="Model path")):
    generate = Generate()
    generate.make_module(model_path, ["model"])
