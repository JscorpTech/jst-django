from rich.progress import Progress, SpinnerColumn, TextColumn


def get_progress():
    return Progress(SpinnerColumn(), TextColumn("{task.description}"))
