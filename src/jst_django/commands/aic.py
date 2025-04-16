from jst_aicommit.main import JstAiCommit
from jst_django.cli.app import app


@app.command(name="aic", help="O'zgarishlarga qarab atomatik git commit yaratadi")
def aic():
    JstAiCommit().run()
