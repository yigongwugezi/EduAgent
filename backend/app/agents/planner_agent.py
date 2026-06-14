from typing import Any

from app.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    agent_id = "planner_agent"
    agent_name = "学习路径规划智能体"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "learning_path": self.mock_data["learning_path"],
            "agent_step": self.agent_step(),
        }
