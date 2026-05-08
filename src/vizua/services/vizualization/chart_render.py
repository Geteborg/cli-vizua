import plotly.express as px
import pandas as pd
from pathlib import Path
import typer

def render_charts(df: pd.DataFrame, candidates: list[dict], output_dir: Path) -> list[dict]:
    """
    Генерирует графики Plotly в темном футуристичном стиле.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for index, candidate in enumerate(candidates, start=1):
        chart_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]
        title = candidate["title"]
        reason = candidate["reason"]
        
        fig = None
        
        try:
            if chart_type == "bar":
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
                # Применяем темную тему и прозрачность для интеграции в дашборд
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", color="#ececec"),
                    title_font=dict(size=18, family="Inter, sans-serif")
                )
                
                clean_title = "".join([c if c.isalnum() else "_" for c in title]).lower()
                file_name = f"{index:02d}_{clean_title}.html"
                file_path = output_dir / file_name
                
                fig.write_html(str(file_path))
                
                results.append({
                    "file_name": file_name,
                    "title": title,
                    "reason": reason,
                    "type": chart_type
                })
                
        except Exception as e:
            typer.echo(f"Ошибка при отрисовке '{title}': {e}", err=True)

    return results

def generate_index_html(output_dir: Path, dataset_name: str, stats: dict, observations: list[str], charts: list[dict]):
    """
    Создает единый HTML-отчет в стиле OpenAI (Dark/Futuristic).
    """
    
    chart_cards = ""
    for chart in charts:
        chart_cards += f"""
        <div class="chart-card">
            <div class="chart-header">
                <h3>{chart['title']}</h3>
                <span class="chart-tag">{chart['type']}</span>
            </div>
            <p class="reason">{chart['reason']}</p>
            <div class="iframe-container">
                <iframe src="{chart['file_name']}" frameborder="0"></iframe>
            </div>
        </div>
        """

    obs_list = "".join([f"<li>{obs}</li>" for obs in observations])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vizua Report: {dataset_name}</title>
        <style>
            :root {{
                --bg: #000000;
                --card-bg: #0a0a0a;
                --card-border: #1f1f1f;
                --text-main: #ececec;
                --text-muted: #7d7d7d;
                --accent: #fff;
                --font-mono: 'SF Mono', 'Fira Code', 'Menlo', monospace;
            }}
            body {{ 
                font-family: 'Inter', -apple-system, sans-serif; 
                background-color: var(--bg); 
                color: var(--text-main); 
                margin: 0; 
                padding: 40px 20px;
                line-height: 1.5;
            }}
            .container {{ max-width: 1300px; margin: 0 auto; }}
            
            header {{ 
                margin-bottom: 60px;
                border-bottom: 1px solid var(--card-border);
                padding-bottom: 30px;
            }}
            h1 {{ 
                font-size: 32px; 
                font-weight: 500; 
                letter-spacing: -0.02em;
                margin: 0 0 20px 0;
            }}
            
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
                gap: 20px; 
            }}
            .stat-box {{ 
                background: var(--card-bg); 
                padding: 20px; 
                border-radius: 4px; 
                border: 1px solid var(--card-border);
            }}
            .stat-value {{ 
                font-family: var(--font-mono);
                font-size: 28px; 
                font-weight: 500; 
                color: var(--accent); 
                margin-bottom: 4px;
            }}
            .stat-label {{ 
                font-size: 12px; 
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--text-muted); 
            }}
            
            .observations {{ 
                background: var(--card-bg); 
                padding: 30px; 
                border-radius: 4px; 
                border: 1px solid var(--card-border);
                margin-bottom: 40px; 
            }}
            .observations h2 {{ 
                font-size: 18px; 
                margin-top: 0; 
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .observations ul {{ padding-left: 20px; color: var(--text-main); }}
            .observations li {{ margin-bottom: 10px; }}
            
            .charts-grid {{ 
                display: grid; 
                grid-template-columns: 1fr; 
                gap: 30px; 
            }}
            @media (min-width: 1000px) {{ .charts-grid {{ grid-template-columns: 1fr 1fr; }} }}
            
            .chart-card {{ 
                background: var(--card-bg); 
                padding: 24px; 
                border-radius: 4px; 
                border: 1px solid var(--card-border);
                display: flex; 
                flex-direction: column; 
            }}
            .chart-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 8px;
            }}
            .chart-card h3 {{ 
                margin: 0; 
                font-size: 18px; 
                font-weight: 500;
            }}
            .chart-tag {{
                font-family: var(--font-mono);
                font-size: 10px;
                text-transform: uppercase;
                background: #1a1a1a;
                padding: 2px 8px;
                border-radius: 2px;
                color: var(--text-muted);
            }}
            .reason {{ 
                font-size: 13px; 
                color: var(--text-muted); 
                margin-bottom: 24px; 
                min-height: 40px;
            }}
            
            .iframe-container {{ 
                flex-grow: 1; 
                height: 500px; 
                background: #000;
                border: 1px solid #151515;
                border-radius: 2px;
            }}
            iframe {{ width: 100%; height: 100%; border: none; }}
            
            footer {{ 
                text-align: left; 
                margin-top: 80px; 
                color: var(--text-muted); 
                font-size: 11px; 
                border-top: 1px solid var(--card-border);
                padding-top: 20px;
                font-family: var(--font-mono);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Vizua. <span style="color:var(--text-muted)">Analysis Report</span></h1>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{stats['rows']}</div>
                        <div class="stat-label">Entries</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{stats['cols']}</div>
                        <div class="stat-label">Dimensions</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{len(charts)}</div>
                        <div class="stat-label">Visuals</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Dataset</div>
                        <div class="stat-value" style="font-size: 14px; margin-top: 8px; overflow: hidden; text-overflow: ellipsis;">{dataset_name}</div>
                    </div>
                </div>
            </header>

            <section class="observations">
                <h2>Insights</h2>
                <ul>{obs_list}</ul>
            </section>

            <section class="charts-grid">
                {chart_cards}
            </section>
            
            <footer>
                VIZUA_CLI_v0.1.0 // DATA_VISUALIZATION_ENGINE
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
