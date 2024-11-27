from typing import List, Union, Optional
import questionary.question
import os
import questionary
import black, isort


class Generate:
    name: Optional[str] = None
    file_name: Optional[str] = None

    def __init__(self) -> None:
        self.path = {
            "apps": "./core/apps/",
            "model": "models/",
            "serializer": "serializers/",
            "view": "views/",
            "permission": "permissions/",
            "admin": "admin/",
            "test": "tests/",
            "translation": "translation/",
            "validator": "validators/",
            "form": "forms/",
            "filter": "filters/",
            "signal": "signals/",
            "stubs": os.path.join(os.path.dirname(__file__), "stubs"),
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
        }

    def directory_ls(self, path: Union[str], ignore_init=True) -> List[str]:
        """Directory items list"""
        response = os.listdir(path)
        if ignore_init:
            response.remove("__init__.py")
        response.remove("logs")
        return response

    def format_code(self, file_path: Union[str]) -> None:
        """Black and Isort format code"""
        isort.settings.Config(profile="black", line_length=120)
        with open(file_path, "r") as file:
            code = isort.code(black.format_str(file.read(), mode=black.FileMode()))
        with open(file_path, "w") as file:
            file.write(code)

    def get_apps(self) -> List[str]:
        """Get django apps"""
        return self.directory_ls(self.path["apps"])

    def get_stub(self, name: Union[str], append: Union[bool] = False) -> str:
        """Get stub"""
        response = ""
        top_content = ""
        with open(os.path.join(self.path["stubs"], self.stubs[name])) as file:
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

    def get_module_name(self, prefix: Union[str] = ""):
        return f"{str(self.name).capitalize()}{prefix}"

    def write_file(
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
            top_content, content = self.get_stub(stub, append=append)
            file.seek(0)
            file.write(top_content.format(name_cap=self.name.capitalize(), file_name=self.file_name))
            file.write(file_content)
            file.write(
                content.format(
                    class_name=self.get_module_name(prefix),
                    name=self.name,
                    name_cap=self.name.capitalize(),
                )
            )

    def make_dir_if_not(self, path):
        """Agar papka mavjud bo'lmasa yaratadi"""
        if not os.path.exists(path):
            os.makedirs(path)

    def import_init(self, init_path: Union[str], file_name: Union[str]):
        with open(init_path, "a") as file:
            file.write(self.get_stub("init")[1].format(file_name=file_name))
        self.format_code(init_path)

    def make_folders(self, app: Union[str], modules: Union[List[str]]) -> bool:
        """Agar kerakli papkalar topilmasa yaratadi"""
        apps_dir = os.path.join(self.path["apps"], app)
        for module in modules:
            module_dir = os.path.join(apps_dir, self.path[module])
            file_path = os.path.join(module_dir, f"{self.file_name}.py")
            init_path = os.path.join(module_dir, "__init__.py")
            self.make_dir_if_not(module_dir)
            if module == "serializer":
                module_dir = os.path.join(module_dir, self.file_name)
                file_path = os.path.join(module_dir, f"{self.name}.py")
                self.make_dir_if_not(module_dir)
                self.import_init(os.path.join(module_dir, "__init__.py"), file_name=self.name)
            if not os.path.exists(file_path):
                self.import_init(init_path, self.file_name)
                self.write_file(file_path, module, module.capitalize())
            else:
                self.write_file(file_path, module, module.capitalize(), append=True)
            self.format_code(file_path)
        return True

    def run(self) -> None:
        """Ishga tushurish uchun"""
        self.file_name = questionary.text("File Name: ").ask()
        self.name = questionary.text("Name: ").ask()

        app = questionary.select("Appni tanlang", choices=self.get_apps()).ask()
        modules = questionary.checkbox("Kerakli modullarni tanlang", self.modules).ask()
        self.make_folders(app, modules)
