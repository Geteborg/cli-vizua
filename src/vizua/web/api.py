from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from vizua.web.endpoints import router as api_router
from vizua.web.endpoints_ai import router as api_ai_router

app = FastAPI(
    title="vizua Web API",
    description="ИИ-сервис автоматического профилирования и визуализации данных",
    version="0.1.0"
)

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем API эндпоинты
app.include_router(api_router)
app.include_router(api_ai_router)


# Путь к статическому веб-интерфейсу
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
def serve_spa():
    """
    Отдает главную страницу SPA-интерфейса.
    """
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"message": "vizua Web API работает. Скомпилированный статический веб-интерфейс не найден."}
