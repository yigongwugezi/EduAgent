from abc import ABC, abstractmethod
from typing import Any

from app.services.llm_client import BaseLLMClient


class BaseAgent(ABC):
    """Common contract for all stage-1 agents."""

    agent_id: str
    agent_name: str

    def __init__(self, mock_data: dict[str, Any], llm_client: BaseLLMClient | None = None) -> None:
        self.mock_data = mock_data
        self.llm_client = llm_client

    @abstractmethod
    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run the agent and return partial result fields."""

    def agent_step(self) -> dict[str, Any]:
        for step in self.mock_data.get("agent_steps", []):
            if step.get("agent_id") == self.agent_id:
                return step

        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": "completed",
            "summary": "Agent completed.",
            "started_at": None,
            "finished_at": None,
        }
