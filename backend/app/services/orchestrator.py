import copy
import json

from app.agents import (
    DiagnosisAgent,
    KnowledgeAgent,
    PlannerAgent,
    ProfileAgent,
    ResourceAgent,
    ReviewAgent,
)
from app.config import settings
from app.services.llm_client import get_llm_client


class AgentOrchestrator:
    """Coordinates the stage-1 multi-agent learning workflow."""

    def __init__(self) -> None:
        self.mock_file = settings.project_root / "backend" / "app" / "mock" / "demo_result.json"

    def run(self, session_id: str, course_id: str, user_message: str) -> dict:
        with self.mock_file.open("r", encoding="utf-8") as file:
            mock_data = json.load(file)["data"]

        context = {
            "session_id": session_id,
            "course_id": course_id,
            "user_message": user_message,
        }

        result = copy.deepcopy(context)
        result["agent_steps"] = []

        for agent in self._build_agents(mock_data):
            partial = agent.run({**context, **result})
            agent_step = partial.pop("agent_step")
            result.update(partial)
            result["agent_steps"].append(agent_step)

        return result

    def _build_agents(self, mock_data: dict) -> list:
        llm_client = get_llm_client(settings.llm_provider)
        return [
            ProfileAgent(mock_data, llm_client=llm_client),
            KnowledgeAgent(mock_data),
            DiagnosisAgent(mock_data),
            PlannerAgent(mock_data),
            ResourceAgent(mock_data),
            ReviewAgent(mock_data),
        ]
