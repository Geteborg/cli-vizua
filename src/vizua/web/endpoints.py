from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
import pandas as pd
from typing import Optional
from pathlib import Path
import tempfile

from vizua.web.dataset_manager import dataset_manager
from vizua.services.profiling.dataset_profiler import profile_dataset
from vizua.services.profiling.advanced_profiler import advanced_profiling
from vizua.services.profiling.profile_diagnostics import profile_diagnostics
from vizua.services.vizualization.chart_pair_generator import generate_pairs
from vizua.services.vizualization.chart_ranker import rank_pairs
from vizua.services.vizualization.chart_selector import select_top_candidates
from vizua.services.vizualization.chart_render import render_charts, render_charts_to_json, generate_index_html

import numpy as np

router = APIRouter(prefix="/api/v1")


def clean_for_json(obj):
    """
    Рекурсивно преобразует numpy-типы в нативные типы Python для безошибочного JSON-кодирования.
    """
    if isinstance(obj, dict):
        return {str(k): clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    elif pd.isna(obj):
        return None
    return obj


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Загрузка CSV датасета.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Поддерживаются только .csv файлы")

    content = await file.read()
    try:
        dataset_id = dataset_manager.add_dataset(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    dataset_item = dataset_manager.get_dataset(dataset_id)
    df: pd.DataFrame = dataset_item["df"]

    # Формируем предпросмотр первых 10 строк
    preview_data = df.head(10).fillna("").to_dict(orient="records")

    return clean_for_json({
        "dataset_id": dataset_id,
        "filename": file.filename,
        "rows": df.shape[0],
        "cols": df.shape[1],
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "preview": preview_data
    })


@router.get("/datasets")
def list_datasets():
    """
    Список загруженных датасетов.
    """
    return dataset_manager.list_datasets()


@router.get("/datasets/{dataset_id}/profile")
def get_profile(dataset_id: str):
    """
    Анализ структуры датасета и профилирование.
    """
    df = dataset_manager.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    basic_results = profile_dataset(df)
    full_results = advanced_profiling(df, basic_results)
    observations = profile_diagnostics(full_results)

    return clean_for_json({
        "dataset_id": dataset_id,
        "basic": full_results.get("basic", {}),
        "missing": full_results.get("missing", {}),
        "unique": full_results.get("unique", {}),
        "advanced": full_results.get("advanced", {}),
        "observations": observations
    })


@router.get("/datasets/{dataset_id}/recommend")
def get_recommendations(dataset_id: str, top: int = Query(5, ge=1, le=20)):
    """
    Получение рекомендаций по визуализации.
    """
    df = dataset_manager.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    basic_results = profile_dataset(df)
    results = advanced_profiling(df, basic_results)
    candidates = generate_pairs(results)
    scored_candidates = rank_pairs(candidates, results, top)
    top_candidates = select_top_candidates(scored_candidates, top)

    return clean_for_json({
        "dataset_id": dataset_id,
        "top": top,
        "total_candidates": len(candidates),
        "recommendations": top_candidates
    })


@router.get("/datasets/{dataset_id}/charts")
def get_charts(dataset_id: str, top: int = Query(5, ge=1, le=20)):
    """
    Получение данных графиков Plotly в формате JSON.
    """
    df = dataset_manager.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    basic_results = profile_dataset(df)
    results = advanced_profiling(df, basic_results)
    candidates = generate_pairs(results)
    scored_candidates = rank_pairs(candidates, results, top)
    top_candidates = select_top_candidates(scored_candidates, top)

    charts_json = render_charts_to_json(df, top_candidates)

    return clean_for_json({
        "dataset_id": dataset_id,
        "count": len(charts_json),
        "charts": charts_json
    })



@router.get("/datasets/{dataset_id}/export/html", response_class=HTMLResponse)
def export_html_report(dataset_id: str, top: int = Query(5, ge=1, le=20)):
    """
    Генерация и скачивание готового автономного HTML-отчета.
    """
    item = dataset_manager.get_dataset(dataset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    df = item["df"]
    filename = item["filename"]

    basic_results = profile_dataset(df)
    results = advanced_profiling(df, basic_results)
    observations = profile_diagnostics(results)

    candidates = generate_pairs(results)
    scored_candidates = rank_pairs(candidates, results, top)
    top_candidates = select_top_candidates(scored_candidates, top)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        chart_info = render_charts(df, top_candidates, tmp_path)
        
        basic_stats = {
            "rows": results["basic"]["rows"],
            "cols": results["basic"]["cols"]
        }
        
        generate_index_html(
            output_dir=tmp_path,
            dataset_name=filename,
            stats=basic_stats,
            observations=observations,
            charts=chart_info
        )
        
        index_file = tmp_path / "index.html"
        if index_file.exists():
            content = index_file.read_text(encoding="utf-8")
            return HTMLResponse(
                content=content,
                headers={
                    "Content-Disposition": f'attachment; filename="vizua_report_{dataset_id}.html"'
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Ошибка при генерации отчета")
