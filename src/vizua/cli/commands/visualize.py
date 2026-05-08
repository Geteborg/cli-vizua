import typer
from pathlib import Path

from vizua.infrastructure.readers.csv_reader import read_csv_file
from vizua.services.profiling.dataset_profiler import profile_dataset
from vizua.services.profiling.advanced_profiler import advanced_profiling
from vizua.services.vizualization.chart_pair_generator import generate_pairs
from vizua.services.vizualization.chart_ranker import rank_pairs
from vizua.services.vizualization.chart_selector import select_top_candidates
from vizua.services.vizualization.chart_render import render_charts


def visualize(file_path: str, output_path: Path, top: int = 3) -> None:
    """
    Полный цикл: чтение, анализ, подбор и генерация графиков в HTML.
    """
    try:
        df = read_csv_file(file_path)
    except Exception as e:
        typer.echo(f"Ошибка чтения файла: {e}")
        raise typer.Exit(code=1)

    typer.echo("📊 Шаг 1: Профилирование данных...")
    sub_results = profile_dataset(df)
    results = advanced_profiling(df, sub_results)

    typer.echo("🤖 Шаг 2: Подбор лучших визуализаций...")
    candidates = generate_pairs(results)
    scored_candidates = rank_pairs(candidates, results, top)
    top_candidates = select_top_candidates(scored_candidates, top)

    if not top_candidates:
        typer.echo("Ни одной подходящей визуализации не найдено.")
        return

    typer.echo(f"🎨 Шаг 3: Генерация графиков (топ-{len(top_candidates)})...")
    saved_files = render_charts(df, top_candidates, output_path)

    if saved_files:
        typer.echo(f"\n✅ Готово! Создано {len(saved_files)} графиков.")
        typer.echo(f"📂 Папка с результатами: {output_path.absolute()}")
        for i, path in enumerate(saved_files, 1):
            typer.echo(f"  {i}. {path.name}")
    else:
        typer.echo("⚠️ Не удалось сохранить ни одного графика.")
