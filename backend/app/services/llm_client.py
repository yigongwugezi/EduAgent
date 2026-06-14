from abc import ABC, abstractmethod
import json
from typing import Any
from urllib import request

from app.config import settings


class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        return "Mock LLM response for Stage 1."


class DeepSeekLLMClient(BaseLLMClient):
    """OpenAI-compatible DeepSeek client used by stage-1 agents."""

    def __init__(self, api_key: str, base_url: str, model: str, temperature: float) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured.")

        payload: dict[str, Any] = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
        }
        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=kwargs.get("timeout", 30)) as response:
            body = json.loads(response.read().decode("utf-8"))

        return body["choices"][0]["message"]["content"]


def get_llm_client(provider: str = "mock") -> BaseLLMClient:
    if provider == "mock":
        return MockLLMClient()
    if provider == "deepseek":
        return DeepSeekLLMClient(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")
