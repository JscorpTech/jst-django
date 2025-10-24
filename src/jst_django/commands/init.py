from jst_django.cli.app import app
from jst_django.utils import Jst


@app.command(name="init", help="jst.json config faylini yaratish")
def init():
    Jst().make_config()
