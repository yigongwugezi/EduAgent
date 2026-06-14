from typing import Any

from app.agents.base import BaseAgent


class KnowledgeAgent(BaseAgent):
    agent_id = "knowledge_agent"
    agent_name = "知识库检索智能体"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        weak_points = self.mock_data["diagnosis"].get("weak_knowledge_points", [])
        retrieved_points = [
            {
                "point_id": item.get("point_id"),
                "name": item.get("name"),
                "priority": item.get("priority"),
            }
            for item in weak_points
        ]

        return {
            "knowledge_context": {
                "course_id": context["course_id"],
                "retrieved_points": retrieved_points,
                "source": "stage1_mock_knowledge_base",
            },
            "agent_step": self.agent_step(),
        }
