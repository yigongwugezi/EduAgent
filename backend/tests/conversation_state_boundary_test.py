import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.conversation_state import ConversationState, ConversationStore


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def facts_after(*messages: str) -> dict[str, str]:
    store = ConversationStore()
    state = ConversationState(session_id="conversation_state_boundary")
    for message in messages:
        store.extract_facts(state, message)
    return state.facts


def test_course_and_period_from_single_message() -> None:
    facts = facts_after("我想一个月学微积分")
    assert_true(facts.get("target_course") == "微积分", "target_course should be 微积分")
    assert_true("一个月" in facts.get("time_budget", ""), "time_budget should keep 一个月")


def test_time_goal_do_not_overwrite_course() -> None:
    facts = facts_after("我想一个月学微积分", "每天三小时，周末休息", "目标期末高分")
    assert_true(facts.get("target_course") == "微积分", "target_course should remain 微积分")
    time_budget = facts.get("time_budget", "")
    assert_true("一个月" in time_budget, "time_budget should keep 一个月")
    assert_true("每天三小时" in time_budget, "time_budget should keep 每天三小时")
    assert_true("周末休息" in time_budget, "time_budget should keep 周末休息")
    assert_true("期末高分" in facts.get("learning_goal", ""), "learning_goal should keep 期末高分")


def test_goal_words_do_not_become_course() -> None:
    for message in ["主要是复习", "目标期末高分", "我想从入门开始", "我想掌握核心题型"]:
        facts = facts_after("我想学微积分", message)
        assert_true(facts.get("target_course") == "微积分", f"{message} should not overwrite target_course")


def test_explicit_course_override() -> None:
    cases = {
        "不是学微积分了，改成数据结构": "数据结构",
        "我不学微积分了，换成线性代数": "线性代数",
        "现在改学 Python": "Python",
    }
    for message, expected in cases.items():
        facts = facts_after("我想学微积分", message)
        assert_true(facts.get("target_course") == expected, f"{message} should override target_course")


def test_weak_points_do_not_overwrite_course() -> None:
    facts = facts_after("我想学微积分", "极限没学过")
    assert_true(facts.get("target_course") == "微积分", "weak point should not overwrite target_course")
    assert_true("极限" in facts.get("weak_points", ""), "weak_points should include 极限")

    facts = facts_after("我想学数据结构", "链表不会", "递归不太懂")
    assert_true(facts.get("target_course") == "数据结构", "weak points should not overwrite target_course")
    assert_true("链表" in facts.get("weak_points", ""), "weak_points should include 链表")
    assert_true("递归" in facts.get("weak_points", ""), "weak_points should include 递归")


def test_supported_course_phrases() -> None:
    cases = {
        "我想学习微积分": "微积分",
        "我准备复习微积分": "微积分",
        "我想学数据结构": "数据结构",
        "我想学习 Python": "Python",
        "我想准备考研英语": "考研英语",
    }
    for message, expected in cases.items():
        facts = facts_after(message)
        assert_true(facts.get("target_course") == expected, f"{message} should extract {expected}")


if __name__ == "__main__":
    test_course_and_period_from_single_message()
    test_time_goal_do_not_overwrite_course()
    test_goal_words_do_not_become_course()
    test_explicit_course_override()
    test_weak_points_do_not_overwrite_course()
    test_supported_course_phrases()
    print("PASS conversation_state_boundary_test")
