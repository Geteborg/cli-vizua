from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from vizua.web.dataset_manager import dataset_manager
from vizua.web.endpoints import clean_for_json
from vizua.services.ai.ai_service import AIService
from vizua.services.profiling.dataset_profiler import profile_dataset
from vizua.services.profiling.advanced_profiler import advanced_profiling
from vizua.services.vizualization.chart_render import render_charts_to_json

router = APIRouter(prefix="/api/v1/ai")


class AIInsightsRequest(BaseModel):
    provider: Optional[str] = "auto"
    api_key: Optional[str] = None
    model: Optional[str] = None


class AIQueryRequest(BaseModel):
    query: str
    provider: Optional[str] = "auto"
    api_key: Optional[str] = None
    model: Optional[str] = None


@router.get("/providers")
def get_providers():
    """
    Возвращает список доступных ИИ-провайдеров и их статусы.
    """
    return AIService.get_available_providers()


@router.post("/datasets/{dataset_id}/insights")
def generate_ai_insights(dataset_id: str, req: AIInsightsRequest):
    """
    Генерация развернутых ИИ-инсайтов для датасета.
    """
    df = dataset_manager.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    basic_results = profile_dataset(df)
    results = advanced_profiling(df, basic_results)

    insights = AIService.generate_insights(
        profile_results=results,
        provider_name=req.provider or "auto",
        api_key=req.api_key,
        model=req.model
    )

    return clean_for_json({
        "dataset_id": dataset_id,
        "provider": req.provider,
        "insights": insights
    })


@router.post("/datasets/{dataset_id}/query")
def query_ai_chart(dataset_id: str, req: AIQueryRequest):
    """
    Текстовый запрос к датасету (Text-to-Viz). Генерирует график Plotly по текстовому описанию.
    """
    df = dataset_manager.get_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Датасет не найден")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Запрос не может быть пустым")

    try:
        chart_candidate = AIService.query_chart_from_text(
            df=df,
            user_query=req.query,
            provider_name=req.provider or "auto",
            api_key=req.api_key,
            model=req.model
        )

        rendered_charts = render_charts_to_json(df, [chart_candidate])
        if not rendered_charts:
            raise HTTPException(status_code=500, detail="Не удалось сгенерировать график по запросу ИИ")

        chart_result = rendered_charts[0]

        return clean_for_json({
            "dataset_id": dataset_id,
            "query": req.query,
            "chart": chart_result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации графика ИИ: {str(e)}")
