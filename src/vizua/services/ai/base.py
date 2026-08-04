from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    json_data: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Абстрактный класс для всех ИИ-провайдеров.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        json_mode: bool = False
    ) -> LLMResponse:
        """
        Отправляет запрос к ИИ-провайдеру и возвращает LLMResponse.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Проверяет доступность провайдера (наличие ключа или доступность сервера).
        """
        pass
