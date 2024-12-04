import isort
from typing import Union
import black


class Code:
    def __init__(self) -> None:
        pass

    @staticmethod
    def format_code(file_path: Union[str]) -> None:
        """Black and Isort format code"""
        isort.settings.Config(profile="black", line_length=120)
        with open(file_path, "r") as file:
            code = isort.code(black.format_str(file.read(), mode=black.FileMode()))
        with open(file_path, "w") as file:
            file.write(code)
