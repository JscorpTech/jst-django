from pathlib import Path


class File:

    def __init__(self) -> None:
        pass

    @staticmethod
    def mkdir(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)
