from jst_django.cli.app import app
from jst_django.utils import Jst


@app.command(name="requirements", help="Kerakli kutubxonalar")
def init():
    Jst().requirements()
