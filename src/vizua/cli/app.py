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

@app.command()
def ask(
    path: Path,
    question: str,
    provider: str = typer.Option("auto", help="Провайдер ИИ: auto, openai, mistral, ollama"),
    model: str = typer.Option(None, help="Модель ИИ (например gpt-4o-mini, mistral-small, llama3)"),
    api_key: str = typer.Option(None, help="API-ключ (если не задан в переменной окружения)")
):
    """Задать вопрос к данным на естественном языке и сгенерировать график."""
    from vizua.infrastructure.readers.csv_reader import read_csv_file
    from vizua.services.ai.ai_service import AIService
    from vizua.services.vizualization.chart_render import render_charts

    try:
        df = read_csv_file(str(path))
    except Exception as e:
        typer.echo(f"Ошибка чтения файла: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"🤖 Обработка запроса ИИ через провайдер [{provider}]...")
    try:
        candidate = AIService.query_chart_from_text(
            df=df,
            user_query=question,
            provider_name=provider,
            api_key=api_key,
            model=model
        )

        output_dir = Path("./charts") / f"{path.stem}_ai_chart"
        rendered = render_charts(df, [candidate], output_dir)

        if rendered:
            typer.echo(f"\n✅ ИИ успешно сгенерировал график!")
            typer.echo(f"   Тип графика: {candidate.get('chart_type')}")
            typer.echo(f"   X: {candidate.get('x')}, Y: {candidate.get('y')}")
            typer.echo(f"   Заголовок: {candidate.get('title')}")
            typer.echo(f"   Причина: {candidate.get('reason')}")
            typer.echo(f"📂 Файл сохранен: {(output_dir / rendered[0]['file_name']).absolute()}")
        else:
            typer.echo("⚠️ Не удалось отрисовать график.")
    except Exception as e:
        typer.echo(f"❌ Ошибка ИИ-генерации: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()


