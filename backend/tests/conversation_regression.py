import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agents.intent_agent import IntentAgent  # noqa: E402
from app.routers import product  # noqa: E402
from app.services.conversation_state import conversation_store  # noqa: E402


def classify(message: str) -> dict:
    return IntentAgent(mock_data={}, llm_client=None).classify(message)


def reply(session_id: str, message: str) -> str:
    state = conversation_store.append_message(session_id, "user", message)
    intent = classify(message)
    conversation_store.set_intent(session_id, intent)
    content, _ = product._reply_for_intent(message, intent, session_id)
    conversation_store.append_message(session_id, "assistant", content)
    assert state.session_id == session_id
    return content


def assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"Expected {expected!r} in:\n{text}")


def assert_not_contains(text: str, unexpected: str) -> None:
    if unexpected in text:
        raise AssertionError(f"Did not expect {unexpected!r} in:\n{text}")


def test_fresh_start_has_no_fake_profile() -> None:
    sid = "regression_fresh_start"
    conversation_store.reset(sid)
    content = reply(sid, "你觉得我该从什么开始")
    assert_contains(content, "还没有你的学习画像")
    assert_not_contains(content, "当前已记录")


def test_profile_update_is_not_casual_chat() -> None:
    sid = "regression_profile_update"
    conversation_store.reset(sid)
    content = reply(sid, "我是软件工程学生")
    assert_contains(content, "身份/专业背景：软件工程学生")
    assert_contains(content, "最想学习哪门课")
    assert_not_contains(content, "我是 EduAgent")


def test_incremental_slot_filling() -> None:
    sid = "regression_slot_filling"
    conversation_store.reset(sid)
    reply(sid, "我是软件工程学生")
    reply(sid, "我想学数据结构")
    state = conversation_store.get(sid)
    assert state.facts["background"] == "软件工程学生"
    assert state.facts["target_course"] == "数据结构"
    assert not conversation_store.readiness(state)["readyToPlan"]

    content = reply(sid, "我数据结构基础一般，链表和树比较薄弱，想两周内做课程实验，更喜欢图解加代码")
    state = conversation_store.get(sid)
    assert conversation_store.readiness(state)["readyToPlan"]
    assert_contains(content, "已经可以生成第一版学习方案")


def test_plan_request_needs_core_profile() -> None:
    sid = "regression_plan_guard"
    conversation_store.reset(sid)
    content = reply(sid, "开始生成学习方案")
    state = conversation_store.get(sid)
    assert "target_course" not in state.facts
    assert_contains(content, "画像信息还不够")
    assert_not_contains(content, "个性化学习方案已生成")


def test_low_value_background_does_not_fill_core_profile() -> None:
    sid = "regression_low_value_background"
    conversation_store.reset(sid)
    content = reply(sid, "我是男生")
    state = conversation_store.get(sid)
    assert "background" not in state.facts
    assert "男生" in state.supplemental_facts.get("personal_background", [])
    assert not conversation_store.readiness(state)["readyToPlan"]
    assert_contains(content, "补充背景")
    assert_contains(content, "不足以决定学习路径")


def test_major_background_fills_core_profile() -> None:
    sid = "regression_major_background"
    conversation_store.reset(sid)
    reply(sid, "我是软件工程学生")
    state = conversation_store.get(sid)
    assert state.facts["background"] == "软件工程学生"
    assert "personal_background" not in state.supplemental_facts


def test_real_dialogue_extracts_time_and_learning_levels() -> None:
    sid = "regression_real_dialogue"
    conversation_store.reset(sid)
    assert classify("我是软件工程大二学生，不会PYTHON，数据结构还可以，线性代数还可以，不会机器学习")["intent"] == "profile_update"
    reply(sid, "我是软件工程大二学生，不会PYTHON，数据结构还可以，线性代数还可以，不会机器学习")
    state = conversation_store.get(sid)
    assert state.facts["background"] == "软件工程大二学生"
    assert "数据结构：还可以" in state.facts["knowledge_base"]
    assert "线性代数：还可以" in state.facts["knowledge_base"]
    assert "PYTHON：不会/不熟" in state.facts["weak_points"]
    assert "机器学习：不会/不熟" in state.facts["weak_points"]

    content = reply(sid, "我想48小时完成")
    state = conversation_store.get(sid)
    assert state.facts["time_budget"] == "48小时完成"
    assert "target_course" not in state.facts
    assert_contains(content, "时间安排：48小时完成")

    reply(sid, "我想学习数据结构，为了考试通过")
    state = conversation_store.get(sid)
    assert state.facts["target_course"] == "数据结构"
    assert "考试" in state.facts["learning_goal"]
    assert conversation_store.readiness(state)["readyToPlan"]


if __name__ == "__main__":
    tests = [
        test_fresh_start_has_no_fake_profile,
        test_profile_update_is_not_casual_chat,
        test_incremental_slot_filling,
        test_plan_request_needs_core_profile,
        test_low_value_background_does_not_fill_core_profile,
        test_major_background_fills_core_profile,
        test_real_dialogue_extracts_time_and_learning_levels,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
