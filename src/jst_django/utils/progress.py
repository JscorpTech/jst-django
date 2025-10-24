from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn


def get_progress():
    return Progress(SpinnerColumn(), TextColumn("{task.description}"))


def cancel():
    print("[bold red]Progress canceled![/bold red]")
