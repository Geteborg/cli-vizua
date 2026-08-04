import json
import pandas as pd
from typing import Optional, Dict, Any, List

from vizua.services.ai.base import BaseLLMProvider, LLMResponse
from vizua.services.ai.openai_provider import OpenAIProvider
from vizua.services.ai.mistral_provider import MistralProvider
from vizua.services.ai.ollama_provider import OllamaProvider
from vizua.services.ai.prompt_builder import build_insights_context


class AIService:
    """
    Менеджер ИИ-провайдеров и функций аналитики/генерации визуализаций.
    """
    @staticmethod
    def get_provider(
        provider_name: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Фабрика ИИ-провайдеров. Поддерживает 'openai', 'mistral', 'ollama', 'auto'.
        """
        name = provider_name.lower().strip()

        if name == "openai":
            return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)
        elif name == "mistral":
            return MistralProvider(api_key=api_key, model=model, base_url=base_url)
        elif name == "ollama":
            return OllamaProvider(api_key=api_key, model=model, base_url=base_url)
        elif name == "auto":
            # 1. Проверяем локальный Ollama
            ollama = OllamaProvider(api_key=api_key, model=model, base_url=base_url)
            if ollama.is_available():
                return ollama
            
            # 2. Проверяем OpenAI
            openai = OpenAIProvider(api_key=api_key, model=model, base_url=base_url)
            if openai.is_available():
                return openai
            
            # 3. Проверяем Mistral
            mistral = MistralProvider(api_key=api_key, model=model, base_url=base_url)
            if mistral.is_available():
                return mistral

            # Фолбэк по умолчанию - Ollama
            return ollama
        else:
            raise ValueError(f"Неизвестный провайдер ИИ: '{provider_name}'. Доступны: openai, mistral, ollama, auto")

    @staticmethod
    def get_available_providers() -> List[Dict[str, Any]]:
        """
        Возвращает статусы доступности всех провайдеров.
        """
        ollama = OllamaProvider()
        openai = OpenAIProvider()
        mistral = MistralProvider()

        return [
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "is_available": ollama.is_available(),
                "requires_api_key": False,
                "local_models": ollama.list_local_models() if ollama.is_available() else []
            },
            {
                "id": "openai",
                "name": "OpenAI API",
                "is_available": openai.is_available(),
                "requires_api_key": True,
                "default_model": "gpt-4o-mini"
            },
            {
                "id": "mistral",
                "name": "Mistral API",
                "is_available": mistral.is_available(),
                "requires_api_key": True,
                "default_model": "mistral-small-latest"
            }
        ]

    @classmethod
    def generate_insights(
        cls, 
        profile_results: dict, 
        provider_name: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[str]:
        """
        Генерирует глубокий текстовый ИИ-анализ на базе профиля датасета.
        """
        provider = cls.get_provider(provider_name=provider_name, api_key=api_key, model=model)
        
        system_prompt = (
            "Ты — опытный senior дата-аналитик. Проанализируй агрегированную статистику датасета "
            "и сформируй от 4 до 7 четких, содержательных текстовых инсайтов на русском языке. "
            "Каждый инсайт должен быть конкретным, выявлять корреляции, аномалии, пропуска или ключевые тренды. "
            "Отвечай только в формате JSON: {\"insights\": [\"Инсайт 1\", \"Инсайт 2\", ...]}"
        )

        compact_ctx = build_insights_context(profile_results)
        prompt = f"Данные профиля датасета:\n{json.dumps(compact_ctx, ensure_ascii=False, indent=2)}"

        try:
            response = provider.generate(prompt=prompt, system_prompt=system_prompt, json_mode=True)
            if response.json_data and "insights" in response.json_data:
                return response.json_data["insights"]
        except Exception as e:
            pass

        # Фолбэк на случай ошибки ИИ
        return [f"ИИ-анализ через провайдер '{provider.provider}': не удалось получить ответ. Проверьте API ключ или локальный сервер."]

    @classmethod
    def query_chart_from_text(
        cls,
        df: pd.DataFrame,
        user_query: str,
        provider_name: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Текстовый запрос к данным (Text-to-Viz). Преобразует вопрос пользователя в параметры Plotly графика.
        """
        provider = cls.get_provider(provider_name=provider_name, api_key=api_key, model=model)

        columns_info = {
            col: str(dtype) for col, dtype in df.dtypes.items()
        }
        sample_rows = df.head(3).to_dict(orient="records")

        system_prompt = (
            "Ты — ИИ-ассистент по визуализации данных. Пользователь хочет построить график на основе текстового запроса. "
            "Подбери наиболее подходящий тип графика (один из: 'bar', 'histogram', 'boxplot', 'scatter'), колонку для оси X, "
            "колонку для оси Y (если требуется) и создай понятный заголовок и объяснение выборки. "
            "Колонки для X и Y ДОЛЖНЫ строго присутствовать в списке доступных колонок датасета!\n"
            "Формат ответа JSON:\n"
            "{\n"
            "  \"chart_type\": \"bar|histogram|boxplot|scatter\",\n"
            "  \"x\": \"название_колонки_X\",\n"
            "  \"y\": \"название_колонки_Y_или_null\",\n"
            "  \"title\": \"Заголовок графика\",\n"
            "  \"reason\": \"Причина выбора графика на русском языке\"\n"
            "}"
        )

        prompt = (
            f"Запрос пользователя: \"{user_query}\"\n\n"
            f"Доступные колонки датасета: {json.dumps(columns_info, ensure_ascii=False)}\n"
            f"Примеры данных (первые 3 строки): {json.dumps(sample_rows, ensure_ascii=False)}"
        )

        response = provider.generate(prompt=prompt, system_prompt=system_prompt, json_mode=True)
        
        if not response.json_data:
            raise ValueError(f"Не удалось распарсить ИИ-ответ: {response.content}")

        chart_spec = response.json_data
        
        # Проверяем валидность указанных колонок
        x_col = chart_spec.get("x")
        if x_col not in df.columns:
            # Автоподбор близкой колонки если нейросеть опечаталась
            for col in df.columns:
                if x_col and x_col.lower() in col.lower():
                    chart_spec["x"] = col
                    break
            else:
                chart_spec["x"] = df.columns[0]

        y_col = chart_spec.get("y")
        if y_col and y_col not in df.columns:
            for col in df.columns:
                if y_col.lower() in col.lower():
                    chart_spec["y"] = col
                    break
            else:
                chart_spec["y"] = None

        return chart_spec
