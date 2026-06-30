import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.orchestrator import AgentOrchestrator


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class ProbeAgent:
    def __init__(self, agent_id: str, payload: dict):
        self.agent_id = agent_id
        self.agent_name = agent_id
        self.payload = payload

    def run(self, context: dict) -> dict:
        return {**self.payload, "agent_step": {"status": "completed", "summary": self.agent_id}}

    def validate_result(self, result: dict) -> None:
        return None


def run_with(agents: list[ProbeAgent]) -> dict:
    orchestrator = AgentOrchestrator()
    orchestrator._build_agents = lambda: agents
    return orchestrator.run(
        session_id="orchestrator_boundary",
        course_id="data_structures",
        user_message="开始生成学习方案",
    )


def test_conversation_only_has_stable_knowledge_context() -> None:
    result = run_with([
        ProbeAgent("conversation_agent", {"action": "none", "intent": "casual_chat", "reply": ""}),
    ])
    assert_true(result["skip_pipeline"] is True, "conversation-only action=none should skip pipeline")
    assert_true(result["pipeline_executed"] is False, "conversation-only should not mark pipeline executed")
    assert_true(result["knowledge_context"]["source"] == "conversation_only", "knowledge source should be stable")
    assert_true(result["agents_run"] == ["conversation_agent"], "agents_run should record executed agents")


def test_action_none_does_not_kill_full_pipeline() -> None:
    result = run_with([
        ProbeAgent("conversation_agent", {"action": "none", "intent": "casual_chat", "reply": ""}),
        ProbeAgent("knowledge_agent", {"knowledge_context": {"source": "course_knowledge_base", "course_id": "data_structures"}}),
        ProbeAgent("planner_agent", {"learning_path": [{"stage_id": "stage_1", "title": "链表"}], "estimatedDays": 2}),
    ])
    assert_true(result["skip_pipeline"] is False, "full pipeline should not be skipped")
    assert_true(result["pipeline_executed"] is True, "full pipeline should be marked executed")
    assert_true("knowledge_agent" in result["agents_run"], "knowledge agent should run")
    assert_true(result["knowledge_context"]["source"] == "course_knowledge_base", "knowledge source should be preserved")
    assert_true(len(result["learning_path"]) == 1, "planner result should be preserved")


def test_full_workflow_action_continues_pipeline() -> None:
    result = run_with([
        ProbeAgent("conversation_agent", {"action": "full_workflow", "intent": "full_workflow", "reply": ""}),
        ProbeAgent("knowledge_agent", {"knowledge_context": {"source": "course_knowledge_base", "course_id": "data_structures"}}),
    ])
    assert_true(result["skip_pipeline"] is False, "full_workflow must not skip")
    assert_true(result["pipeline_executed"] is True, "full_workflow should execute pipeline")


if __name__ == "__main__":
    test_conversation_only_has_stable_knowledge_context()
    test_action_none_does_not_kill_full_pipeline()
    test_full_workflow_action_continues_pipeline()
    print("PASS orchestrator_boundary_test")
