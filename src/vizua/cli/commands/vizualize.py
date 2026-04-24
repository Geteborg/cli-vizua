import typer

from vizua.infrastructure.readers.csv_reader import read_csv_file
from vizua.services.profiling.dataset_profiler import profile_dataset
from vizua.services.profiling.advanced_profiler import advanced_profilling
from vizua.services.vizualization.chart_pair_generator import generate_pairs
from vizua.services.vizualization.chart_ranker import rank_pairs
from vizua.services.vizualization.chart_selector import select_top_candidates


def visualize(file_path: str, top: int = 3) -> None:
    """
    Читает CSV-файл и выводит топ N предложений для построения визуализаций.
    """
    try:
        df = read_csv_file(file_path)
    except Exception as e:
        typer.echo(f"Ошибка: {e}")
        raise typer.Exit(code=1)

    sub_results = profile_dataset(df)

    results = advanced_profilling(df, sub_results)

    candidates = generate_pairs(results)

    scored_candidates = rank_pairs(candidates, results, top)

    top_n_candidates = select_top_candidates(scored_candidates, top)

    if not top_n_candidates:
        typer.echo("Подходящих визуализаций не найдено.")
        raise typer.Exit(code=0)

    chart_type_labels = {
        "bar": "Bar chart",
        "histogram": "Histogram",
        "boxplot": "Box plot",
        "scatter": "Scatter plot",
    }

    lines = []
    lines.append(f"Рекомендуемые визуализации (top {top}):")
    lines.append("")

    for index, candidate in enumerate(top_n_candidates, start=1):
        chart_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]
        score = candidate["score"]
        title = candidate["title"]
        reason = candidate["reason"]

        chart_label = chart_type_labels.get(chart_type, chart_type)

        lines.append(f"{index}. {chart_label}")
        lines.append(f"   X: {x}")
        if y is not None:
            lines.append(f"   Y: {y}")
        lines.append(f"   Score: {score}")
        lines.append(f"   Title: {title}")
        lines.append(f"   Reason: {reason}")
        lines.append("")

    output = "\n".join(lines)
    typer.echo(output)
