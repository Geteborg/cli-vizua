import typer

from vizua.cli.commands.hello import hello
from vizua.cli.commands.version import version
from vizua.cli.commands.describe import describe
from vizua.cli.commands.vizualize import visualize

app = typer.Typer()

app.command()(hello)
app.command()(version)
app.command()(describe)
app.command()(visualize)