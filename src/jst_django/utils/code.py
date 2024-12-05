import isort
from typing import Union
import black


class Code:
    def __init__(self) -> None:
        pass

    @staticmethod
    def format_code(file_path: Union[str]) -> None:
        """Black and Isort format code"""
        with open(file_path, "r") as file:
            code = black.format_str(
                isort.code(file.read(), config=isort.Config(profile="black", line_length=120)),
                mode=black.FileMode(line_length=120),
            )
        with open(file_path, "w") as file:
            file.write(code)
