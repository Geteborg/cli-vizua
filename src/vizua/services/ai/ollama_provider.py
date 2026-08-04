import os
import json
import httpx
from typing import Optional
from vizua.services.ai.base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """
    Провайдер для работы с локальным Ollama сервером (llama3, mistral, qwen2.5, gemma2 и др.).
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        selected_model = model or os.getenv("OLLAMA_MODEL", "llama3")
        url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        super().__init__(api_key=api_key, model=selected_model, base_url=url)

    def is_available(self) -> bool:
        """
        Проверяет доступность локального сервера Ollama по HTTP.
        """
        endpoint = f"{self.base_url.rstrip('/')}/api/tags"
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(endpoint)
                return res.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> list[str]:
        """
        Возвращает список установленных моделей в локальном Ollama.
        """
        endpoint = f"{self.base_url.rstrip('/')}/api/tags"
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(endpoint)
                if res.status_code == 200:
                    data = res.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        json_mode: bool = False
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        if json_mode:
            payload["format"] = "json"

        endpoint = f"{self.base_url.rstrip('/')}/api/chat"

        with httpx.Client(timeout=60.0) as client:
            res = client.post(endpoint, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama Error ({res.status_code}): {res.text}")
            
            data = res.json()
            content = data.get("message", {}).get("content", "")
            
            json_parsed = None
            if json_mode:
                try:
                    json_parsed = json.loads(content)
                except Exception:
                    pass

            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model,
                json_data=json_parsed,
                raw_response=data
            )
