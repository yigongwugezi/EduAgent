from typing import Any

from app.agents.base import BaseAgent


class ReviewAgent(BaseAgent):
    agent_id = "review_agent"
    agent_name = "质量审核智能体"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "review": self.mock_data["review"],
            "agent_step": self.agent_step(),
        }
