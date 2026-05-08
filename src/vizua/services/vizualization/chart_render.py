import plotly.express as px
import pandas as pd
from pathlib import Path
import typer

def render_charts(df: pd.DataFrame, candidates: list[dict], output_dir: Path) -> list[Path]:
    """
    Генерирует графики Plotly на основе списка кандидатов и сохраняет их в HTML.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for index, candidate in enumerate(candidates, start=1):
        chart_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]
        title = candidate["title"]
        
        fig = None
        
        try:
            if chart_type == "bar":
                # Для столбчатых диаграмм агрегируем данные (среднее)
                if y:
                    plot_df = df.groupby(x, observed=True)[y].mean().reset_index()
                    fig = px.bar(plot_df, x=x, y=y, title=title)
                else:
                    fig = px.bar(df, x=x, title=title)
            
            elif chart_type == "histogram":
                fig = px.histogram(df, x=x, title=title)
            
            elif chart_type == "boxplot":
                fig = px.box(df, y=x, title=title)
            
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x, y=y, title=title)
            
            if fig:
                # Очистка имени файла
                clean_title = "".join([c if c.isalnum() else "_" for c in title]).lower()
                file_name = f"{index:02d}_{clean_title}.html"
                file_path = output_dir / file_name
                
                fig.write_html(str(file_path))
                saved_files.append(file_path)
                
        except Exception as e:
            typer.echo(f"Ошибка при отрисовке '{title}': {e}", err=True)

    return saved_files
