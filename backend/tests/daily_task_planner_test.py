"""Test PlannerAgent daily task generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.planner_agent import PlannerAgent


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _profile() -> dict:
    return {
        "major_background": {"value": "软件工程大二学生"},
        "knowledge_base": {"value": "数据结构基础一般"},
        "learning_goal": {"value": "为了考试通过"},
        "cognitive_style": {"value": "喜欢图解和练习题"},
        "learning_rhythm": {"value": "10天完成"},
    }


def test_llm_or_fallback_path_includes_daily_tasks() -> None:
    """Every stage in the planner output must contain a daily_tasks key."""
    result = PlannerAgent().run(
        {
            "session_id": "planner_daily_task_test",
            "course_id": "data_structures",
            "user_message": "我是软件工程大二学生，想10天复习数据结构，喜欢图解和练习题。",
            "profile": _profile(),
            "profile_facts": {
                "background": "软件工程大二学生",
                "target_course": "数据结构",
                "knowledge_base": "数据结构基础一般",
                "learning_goal": "为了考试通过",
                "time_budget": "10天",
                "preference": "图解、练习题",
            },
            "diagnosis": {
                "weak_knowledge_points": [
                    {"name": "栈、队列与递归", "priority": "high"},
                ]
            },
        }
    )

    path = result["learning_path"]
    assert_true(len(path) >= 1, "Should have at least 1 stage")

    for stage in path:
        title = stage.get("title", "unknown")
        assert_true("daily_tasks" in stage, f"Stage '{title}' must have daily_tasks key")
        dt = stage["daily_tasks"]
        assert_true(isinstance(dt, list), f"daily_tasks in '{title}' must be a list")
        assert_true(len(dt) >= 1, f"Stage '{title}' must have at least 1 daily task entry")

        # Verify structure of each daily task entry
        for entry in dt:
            assert_true(isinstance(entry, dict), "Each daily task entry should be a dict")
            assert_true("day" in entry, f"Daily task entry should have 'day': {entry}")
            assert_true("tasks" in entry, f"Daily task entry should have 'tasks': {entry}")
            assert_true(isinstance(entry["tasks"], list),
                        f"'tasks' should be a list: {entry}")
            assert_true(len(entry["tasks"]) >= 1,
                        f"Each day should have at least 1 task: {entry}")
            for t in entry["tasks"]:
                assert_true(isinstance(t, str) and t.strip(),
                            f"Each task should be a non-empty string: {t}")


def test_daily_tasks_respect_duration_range() -> None:
    """Daily task day numbers should fall within the stage's duration."""
    result = PlannerAgent().run(
        {
            "session_id": "planner_daily_duration_test",
            "user_message": "我想用6天学习线性回归。",
            "profile": {"learning_goal": {"value": "学习线性回归"}},
            "diagnosis": {
                "weak_knowledge_points": [],
                "needs_more_evidence": True,
            },
        }
    )

    import re
    path = result["learning_path"]
    for stage in path:
        duration = str(stage.get("duration", ""))
        day_nums = re.findall(r"\d+", duration)

        dt = stage.get("daily_tasks", [])
        if not dt:
            continue

        if len(day_nums) >= 2:
            start_day, end_day = int(day_nums[0]), int(day_nums[1])
        elif len(day_nums) == 1:
            start_day = end_day = int(day_nums[0])
        else:
            continue

        for entry in dt:
            day = entry.get("day", 0)
            assert_true(start_day <= day <= end_day,
                        f"Day {day} should be in range [{start_day}, {end_day}] "
                        f"for stage '{stage.get('title')}' duration='{duration}'")


def test_fallback_daily_tasks_are_marked_rule_fallback() -> None:
    """When no course or diagnosis, fallback stages should have daily_tasks
    with source=rule_fallback."""
    result = PlannerAgent().run(
        {
            "session_id": "planner_fallback_daily_test",
            "user_message": "",
            "diagnosis": {"weak_knowledge_points": [], "needs_more_evidence": True},
        }
    )

    path = result["learning_path"]
    fallback_stages = [s for s in path if s.get("source") == "rule_fallback"]
    assert_true(len(fallback_stages) >= 1,
                "Should have at least 1 rule_fallback stage")

    for stage in fallback_stages:
        dt = stage.get("daily_tasks", [])
        assert_true(len(dt) >= 1,
                    f"Fallback stage '{stage.get('title')}' must have daily_tasks")


def test_daily_tasks_never_contain_placeholder_text() -> None:
    """Daily task titles should never contain internal placeholder text."""
    result = PlannerAgent().run(
        {
            "session_id": "planner_no_placeholder_test",
            "user_message": "帮我安排学习路径。",
            "diagnosis": {
                "weak_knowledge_points": ["无诊断数据"],
                "needs_more_evidence": True,
            },
        }
    )

    for stage in result["learning_path"]:
        dt = stage.get("daily_tasks", [])
        for entry in dt:
            for task in entry.get("tasks", []):
                assert_true("无诊断数据" not in task,
                            f"Task title must not contain placeholder: '{task}'")


if __name__ == "__main__":
    test_llm_or_fallback_path_includes_daily_tasks()
    test_daily_tasks_respect_duration_range()
    test_fallback_daily_tasks_are_marked_rule_fallback()
    test_daily_tasks_never_contain_placeholder_text()
    print("PASS daily_task_planner_test")
