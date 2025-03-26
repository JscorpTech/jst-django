from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print


def get_progress():
    return Progress(SpinnerColumn(), TextColumn("{task.description}"))


def cancel():
    print("[bold red]Progress canceled![/bold red]")
