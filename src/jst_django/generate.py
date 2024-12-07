from typing import List, Union, Optional, Generator
import questionary.question
import os
import questionary
from .utils import File, Code, Jst
from pathlib import Path
from os.path import join


class Generate:
    name: Optional[str] = None
    file_name: Optional[str] = None

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

    def _directory_ls(self, path: Union[str]) -> Generator[Union[Path], None, None]:
        """Directory items list"""
        ignore = ["logs"]
        for item in Path(path).iterdir():
            if item.name not in ignore and item.is_dir():
                yield item

    def _get_apps(self) -> Generator[Union[str], None, None]:
        """Django applar ro'yxatini qaytaradi"""
        dirs = self._directory_ls(self.path["apps"])
        for item in dirs:
            if item.joinpath("apps.py").exists():
                yield item.name

    def __get_stub_path(self, name):
        """Stubfayil manzilini olish"""
        if Path(self.stubs[name]).exists():
            return self.stubs[name]
        path = Path(self.path["stubs"], self.stubs[name])
        if path.exists():
            return path
        raise Exception("Stub fayil mavjud emas")

    def _read_stub(self, name: Union[str], append: Union[bool] = False) -> str:
        """Get stub"""
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

    def _get_module_name(self, prefix: Union[str] = ""):
        return f"{str(self.name).capitalize()}{prefix}"

    def _write_file(
        self,
        file_path: Union[str],
        stub: Union[str],
        prefix: Union[str] = "",
        append: Union[bool] = False,
    ):
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        with open(file_path, "r+") as file:
            file_content = file.read()
            top_content, content = self._read_stub(stub, append=append)
            file.seek(0)
            file.write(top_content.format(name_cap=self.name.capitalize(), file_name=self.file_name))
            file.write(file_content)
            file.write(
                content.format(
                    class_name=self._get_module_name(prefix),
                    name=self.name,
                    name_cap=self.name.capitalize(),
                )
            )

    def _import_init(self, init_path: Union[str], file_name: Union[str]):
        """__init__.py fayliga kerakli fayillarni import qiladi mavjud bo'lmasa yaratadi"""
        with open(init_path, "a") as file:
            file.write(self._read_stub("init")[1].format(file_name=file_name))
        Code.format_code(init_path)

    def make_folders(self, app: Union[str], modules: Union[List[str]]) -> bool:
        """Agar kerakli papkalar topilmasa yaratadi"""
        apps_dir = join(self.path["apps"], app)
        for module in modules:
            module_dir = join(apps_dir, self.path[module])
            file_path = join(module_dir, f"{self.file_name}.py")
            init_path = join(module_dir, "__init__.py")
            File.mkdir(module_dir)
            if module == "serializer":
                module_dir = join(module_dir, self.file_name)
                file_path = join(module_dir, f"{self.name}.py")
                File.mkdir(module_dir)
                self._import_init(join(module_dir, "__init__.py"), file_name=self.name)
            if not os.path.exists(file_path):
                self._import_init(init_path, self.file_name)
                self._write_file(file_path, module, module.capitalize())
            else:
                self._write_file(file_path, module, module.capitalize(), append=True)
            Code.format_code(file_path)
        return True

    def run(self) -> None:
        """Ishga tushurish uchun"""
        self.file_name = questionary.text("File Name: ").ask()
        self.name = questionary.text("Name: ").ask()

        app = questionary.select("Appni tanlang", choices=list(self._get_apps())).ask()
        modules = questionary.checkbox("Kerakli modullarni tanlang", self.modules).ask()
        self.make_folders(app, modules)
