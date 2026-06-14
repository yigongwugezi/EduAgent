from typing import Any

from app.agents.base import BaseAgent


class ResourceAgent(BaseAgent):
    agent_id = "resource_agent"
    agent_name = "学习资源生成智能体"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "resources": self.mock_data["resources"],
            "agent_step": self.agent_step(),
        }
