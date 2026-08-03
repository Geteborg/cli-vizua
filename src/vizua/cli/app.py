import typer
from pathlib import Path
from vizua.cli.commands.describe import describe
from vizua.cli.commands.recommend import recommend as recommend_logic

from vizua.cli.commands.visualize import visualize as run_visualize

app = typer.Typer(help="vizua: ИИ-помощник для визуализации данных")

@app.command()
def profile(path: Path):
    """Анализ структуры данных и поиск проблем."""
    describe(str(path))

@app.command()
def recommend(
    path: Path, 
    top: int = typer.Option(3, help="Количество рекомендаций")
):
    """Получить рекомендации по выбору графиков."""
    recommend_logic(str(path), top=top)

@app.command()
def visualize(
    path: Path, 
    output: Path = typer.Option(Path("./charts"), help="Базовая папка для сохранения"),
    top: int = typer.Option(3, help="Количество графиков для генерации")
):
    """Автоматическая генерация визуализаций в HTML."""
    # Формируем путь: output / {filename}_charts
    subfolder_name = f"{path.stem}_charts"
    final_output = output / subfolder_name
    
    run_visualize(str(path), final_output, top=top)

@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", help="Хост веб-сервера"),
    port: int = typer.Option(8000, help="Порт веб-сервера"),
    open_browser: bool = typer.Option(True, help="Автоматически открыть веб-интерфейс в браузере")
):
    """Запуск локального веб-интерфейса vizua в браузере."""
    import uvicorn
    import webbrowser
    import threading
    import time

    url = f"http://{host}:{port}"
    typer.echo(f"🌐 Запуск веб-интерфейса vizua...")
    typer.echo(f"🔗 Адрес: {url}")
    typer.echo("Для остановки сервера нажмите Ctrl+C\n")

    if open_browser:
        def open_page():
            time.sleep(1.0)
            webbrowser.open(url)

        threading.Thread(target=open_page, daemon=True).start()

    uvicorn.run("vizua.web.api:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    app()

