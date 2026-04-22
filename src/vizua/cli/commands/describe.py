import typer

from vizua.infrastructure.readers.csv_reader import read_csv_file
from vizua.services.profiling.dataset_profiler import profile_dataset
from vizua.services.profiling.profile_diagnostics import profile_diagnostics


def describe(file_path: str) -> None:
    """
    Читает CSV-файл и выводит базовую информацию о датасете.
    """
    try:
        df = read_csv_file(file_path)
    except Exception as e:
        typer.echo (f"Ошибка: {e}")
        raise typer.Exit(code=1)
    
    
    results = profile_dataset(df)

    rows = results["rows"]
    cols = results["cols"]
    columns = results["columns"] 
    dtypes = results["dtypes"]
    missing_by_column = results["missing_by_column"]
    duplicated_rows = results["duplicated_rows"]
    unique_by_column = results["unique_by_column"]


    lines = []

    lines.append(f"Файл успешно прочитан: {file_path}")
    lines.append("")

    lines.append("Общая информация:")
    lines.append(f"- строк: {rows}")
    lines.append(f"- столбцов: {cols}")
    lines.append("")

    lines.append("Колонки:")
    for column in columns:
        lines.append(f"- {column}")
    lines.append("")

    lines.append("Типы данных:")
    for column, dtype in dtypes.items():
        lines.append(f"- {column}: {dtype}")
    lines.append("")

    lines.append("Пропуски:")
    for column, missing_count in missing_by_column.items():
        lines.append(f"- {column}: {missing_count}")
    lines.append("")

    lines.append("Уникальные значения:")
    for column, unique_count in unique_by_column.items():
        lines.append(f"- {column}: {unique_count}")
    lines.append("")

    lines.append("Дубликаты:")
    lines.append(f"- {duplicated_rows}")

    diagnose = profile_diagnostics(results)

    lines.append("")
    lines.append("Наблюдения:")
    for item in diagnose:
        lines.append(f"- {item}")

    output = "\n".join(lines)
    typer.echo(output)