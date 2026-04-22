import typer


def version() -> None:
    """
    Выводит версию CLI.
    """
    typer.echo("Моя версия - 0.0.0.1 beta")