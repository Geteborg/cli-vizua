from fastapi.testclient import TestClient
from vizua.web.api import app
import pytest
import io

client = TestClient(app)


def test_serve_spa():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Vizua Web" in response.text


def test_upload_and_full_api_flow():
    # Создаем фиктивный CSV контент
    csv_content = (
        "category,value,sales,id\n"
        "A,10,100,1\n"
        "B,20,200,2\n"
        "A,15,150,3\n"
        "C,30,300,4\n"
        "B,25,250,5\n"
    ).encode("utf-8")

    # 1. Загрузка CSV
    files = {"file": ("test_sales.csv", io.BytesIO(csv_content), "text/csv")}
    upload_res = client.post("/api/v1/upload", files=files)
    assert upload_res.status_code == 200
    data = upload_res.json()
    assert "dataset_id" in data
    assert data["rows"] == 5
    assert data["cols"] == 4
    dataset_id = data["dataset_id"]

    # 2. Профилирование
    profile_res = client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["basic"]["rows"] == 5
    assert len(profile_data["observations"]) > 0

    # 3. Рекомендации
    recommend_res = client.get(f"/api/v1/datasets/{dataset_id}/recommend?top=3")
    assert recommend_res.status_code == 200
    rec_data = recommend_res.json()
    assert len(rec_data["recommendations"]) <= 3

    # 4. JSON графиков Plotly
    charts_res = client.get(f"/api/v1/datasets/{dataset_id}/charts?top=3")
    assert charts_res.status_code == 200
    charts_data = charts_res.json()
    assert "charts" in charts_data
    assert len(charts_data["charts"]) > 0
    chart_item = charts_data["charts"][0]
    assert "plotly_json" in chart_item
    assert "data" in chart_item["plotly_json"]

    # 5. Экспорт HTML отчета
    export_res = client.get(f"/api/v1/datasets/{dataset_id}/export/html?top=3")
    assert export_res.status_code == 200
    assert "Vizua Report:" in export_res.text
