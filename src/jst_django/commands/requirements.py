from jst_django.utils import Jst
from jst_django.cli.app import app


@app.command(name="requirements", help="Kerakli kutubxonalar")
def init():
    Jst().requirements()
