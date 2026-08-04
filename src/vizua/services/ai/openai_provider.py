import os
import json
import httpx
from typing import Optional
from vizua.services.ai.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """
    Провайдер для работы с OpenAI API (GPT-4o, GPT-4o-mini).
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        key = api_key or os.getenv("OPENAI_API_KEY", "")
        selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        super().__init__(api_key=key, model=selected_model, base_url=url)

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        json_mode: bool = False
    ) -> LLMResponse:
        if not self.is_available():
            raise ValueError("OPENAI_API_KEY не установлен.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"

        with httpx.Client(timeout=40.0) as client:
            res = client.post(endpoint, headers=headers, json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"OpenAI API Error ({res.status_code}): {res.text}")
            
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            
            json_parsed = None
            if json_mode:
                try:
                    json_parsed = json.loads(content)
                except Exception:
                    pass

            return LLMResponse(
                content=content,
                provider="openai",
                model=self.model,
                json_data=json_parsed,
                raw_response=data
            )
