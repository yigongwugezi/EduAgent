from typing import Any

from app.agents.base import BaseAgent


class DiagnosisAgent(BaseAgent):
    agent_id = "diagnosis_agent"
    agent_name = "学习诊断智能体"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "diagnosis": self.mock_data["diagnosis"],
            "agent_step": self.agent_step(),
        }
