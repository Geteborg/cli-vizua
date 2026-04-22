import typer


def hello(name: str = "World", formal: bool = False) -> None:
    """
    Приветствие пользователя.
    """
    if formal:
        typer.echo(f"Здравствуйте, {name}.")
    else:
        typer.echo(f"Здарова, {name}, брат.")