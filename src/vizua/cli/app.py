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

if __name__ == "__main__":
    app()
