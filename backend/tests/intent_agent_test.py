import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.intent_agent import IntentAgent  # noqa: E402
from app.services.llm_client import BaseLLMClient, LLMClientError, MockLLMClient  # noqa: E402


class IntentJSONLLM(BaseLLMClient):
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        return json.dumps(
            {
                "primary_intent": "diagnosis",
                "secondary_intents": ["learning_plan"],
                "confidence": 0.81,
                "reason": "The learner asks what to repair next, which implies diagnosis.",
                "should_run_full_workflow": False,
                "needs_subject": False,
                "needs_clarification": False,
                "clarification_question": None,
                "extracted": {
                    "subject_name": None,
                    "time_budget": None,
                    "learning_goal": None,
                    "current_level": None,
                    "weak_topic": None,
                    "requested_outputs": ["diagnosis"],
                },
            },
            ensure_ascii=False,
        )


class FailingLLM(BaseLLMClient):
    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        raise LLMClientError("intent classifier unavailable")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_explicit_diagnosis_keeps_legacy_intent_and_structured_fields() -> None:
    result = IntentAgent(llm_client=MockLLMClient()).classify("我哪里比较薄弱？")
    assert_true(result["intent"] == "diagnosis", "explicit weakness question should route to diagnosis")
    assert_true(result["primary_intent"] == "diagnosis", "primary_intent should be diagnosis")
    assert_true("confidence" in result and result["confidence"] > 0, "confidence should be present")
    assert_true(result["reason"], "intent reason should not be empty")
    assert_true(isinstance(result["extracted"], dict), "extracted should be a stable object")


def test_full_workflow_has_secondary_intents_and_extracted_fields() -> None:
    result = IntentAgent(llm_client=MockLLMClient()).classify(
        "我是计算机新生，Python 基础比较弱，我想用 2 天入门 Python，请帮我构建学习画像、学习路径和学习资源。"
    )
    assert_true(result["intent"] == "full_workflow", "compound request should stay full_workflow")
    assert_true(result["should_run_full_workflow"] is True, "full workflow flag should be true")
    for intent in ("profile_update", "learning_plan", "resource_request"):
        assert_true(intent in result["secondary_intents"], f"missing secondary intent: {intent}")
    assert_true(result["extracted"]["subject_name"] == "Python", "subject should be extracted")
    assert_true(result["extracted"]["time_budget"] == "2 天", "time budget should be extracted")
    assert_true(result["extracted"]["weak_topic"] == "Python", "weak topic should be extracted")


def test_implicit_diagnosis_uses_llm_assisted_classification() -> None:
    result = IntentAgent(llm_client=IntentJSONLLM()).classify("我感觉最近学得很乱，不知道该补哪里。")
    assert_true(result["intent"] == "diagnosis", "implicit weakness request should route to diagnosis")
    assert_true(result["source"] == "llm_generated", "real LLM JSON classification should be marked")
    assert_true("learning_plan" in result["secondary_intents"], "follow-up planning should be a secondary intent")
    assert_true(result["confidence"] >= 0.7, "LLM confidence should be retained")


def test_resource_request_is_stable() -> None:
    result = IntentAgent(llm_client=MockLLMClient()).classify("给我一些适合我现在阶段的练习和资料。")
    assert_true(result["intent"] == "resource_request", "practice/material request should route to resources")
    assert_true(result["should_run_agents"] is True, "resource request should run agents")
    assert_true("resources" in result["extracted"]["requested_outputs"], "requested resources should be extracted")


def test_new_subject_expression_extracts_subject() -> None:
    result = IntentAgent(llm_client=MockLLMClient()).classify("我想学操作系统。")
    assert_true(result["intent"] == "learning_plan", "new subject expression should be plannable")
    assert_true(result["needs_subject"] is True, "subject handoff should be explicit")
    assert_true(result["extracted"]["subject_name"] == "操作系统", "subject_name should be extracted")


def test_vague_request_asks_for_clarification() -> None:
    result = IntentAgent(llm_client=MockLLMClient()).classify("帮我安排一下。")
    assert_true(result["needs_clarification"] is True, "vague request should ask for clarification")
    assert_true(result["clarification_question"], "clarification question should be present")
    assert_true(result["intent"] == "unknown", "vague request should not be over-routed")


def test_llm_failure_falls_back_to_rules() -> None:
    result = IntentAgent(llm_client=FailingLLM()).classify("帮我生成学习路径")
    assert_true(result["intent"] == "learning_plan", "LLM failure should fall back to rule-based routing")
    assert_true(result["source"] in {"rule_based", "rule_based_fallback"}, "fallback source should be explicit")
    assert_true(result["reason"], "fallback reason should be retained")


if __name__ == "__main__":
    test_explicit_diagnosis_keeps_legacy_intent_and_structured_fields()
    test_full_workflow_has_secondary_intents_and_extracted_fields()
    test_implicit_diagnosis_uses_llm_assisted_classification()
    test_resource_request_is_stable()
    test_new_subject_expression_extracts_subject()
    test_vague_request_asks_for_clarification()
    test_llm_failure_falls_back_to_rules()
    print("PASS intent_agent_test")
