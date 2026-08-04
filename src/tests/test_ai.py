import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import io

from vizua.services.ai.ai_service import AIService
from vizua.services.ai.openai_provider import OpenAIProvider
from vizua.services.ai.mistral_provider import MistralProvider
from vizua.services.ai.ollama_provider import OllamaProvider
from vizua.services.ai.base import LLMResponse
from vizua.web.api import app

client = TestClient(app)


def test_provider_availability_and_factory():
    # Проверка получения списка провайдеров
    providers = AIService.get_available_providers()
    assert len(providers) == 3
    provider_ids = [p["id"] for p in providers]
    assert "ollama" in provider_ids
    assert "openai" in provider_ids
    assert "mistral" in provider_ids

    # Фабрика провайдеров
    p_ollama = AIService.get_provider("ollama")
    assert isinstance(p_ollama, OllamaProvider)

    p_openai = AIService.get_provider("openai", api_key="sk-test-12345")
    assert isinstance(p_openai, OpenAIProvider)
    assert p_openai.is_available() is True

    p_mistral = AIService.get_provider("mistral", api_key="mistral-test-12345")
    assert isinstance(p_mistral, MistralProvider)
    assert p_mistral.is_available() is True


@patch.object(OpenAIProvider, "generate")
def test_ai_query_chart_from_text(mock_generate):
    mock_generate.return_value = LLMResponse(
        content='{"chart_type": "scatter", "x": "age", "y": "salary", "title": "Age vs Salary", "reason": "AI matched user intent"}',
        provider="openai",
        model="gpt-4o-mini",
        json_data={
            "chart_type": "scatter",
            "x": "age",
            "y": "salary",
            "title": "Age vs Salary",
            "reason": "AI matched user intent"
        }
    )

    import pandas as pd
    df = pd.DataFrame({
        "age": [25, 30, 35, 40],
        "salary": [50000, 60000, 75000, 90000]
    })

    result = AIService.query_chart_from_text(
        df=df,
        user_query="Show me age vs salary scatter plot",
        provider_name="openai",
        api_key="sk-test"
    )

    assert result["chart_type"] == "scatter"
    assert result["x"] == "age"
    assert result["y"] == "salary"


def test_ai_api_endpoints_flow():
    # 1. GET /api/v1/ai/providers
    res = client.get("/api/v1/ai/providers")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) == 3

    # 2. Upload dataset first
    csv_content = "age,salary,department\n25,50000,Analytics\n30,70000,Engineering\n".encode("utf-8")
    upload_res = client.post("/api/v1/upload", files={"file": ("test_ai.csv", io.BytesIO(csv_content), "text/csv")})
    assert upload_res.status_code == 200
    dataset_id = upload_res.json()["dataset_id"]

    # 3. POST /api/v1/ai/datasets/{id}/query with mock
    with patch.object(AIService, "query_chart_from_text") as mock_query:
        mock_query.return_value = {
            "chart_type": "bar",
            "x": "department",
            "y": "salary",
            "title": "Salary by Department",
            "reason": "AI recommendation"
        }

        query_res = client.post(f"/api/v1/ai/datasets/{dataset_id}/query", json={
            "query": "Покажи зарплату по отделам",
            "provider": "openai",
            "api_key": "sk-fake-key"
        })

        assert query_res.status_code == 200
        q_data = query_res.json()
        assert "chart" in q_data
        assert q_data["chart"]["type"] == "bar"
        assert q_data["chart"]["x"] == "department"
