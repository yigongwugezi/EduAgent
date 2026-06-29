"""Test daily task repository functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.engine import SessionLocal, init_db
from app.db.models import DailyTaskModel
from app.db.repository import (
    upsert_daily_tasks,
    get_daily_tasks,
    get_daily_tasks_for_learner,
    update_task_completion,
    get_or_create_session,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _setup() -> str:
    """Prepare a session + daily tasks. Returns session_id."""
    init_db()
    db = SessionLocal()
    session_id = "test_daily_task_db_session"
    learner_id = "test_daily_task_learner"
    get_or_create_session(db, session_id, learner_id=learner_id, subject_id="ai_intro")

    tasks = [
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "学习基础概念", "source": "agent_generated"},
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "完成课后练习", "source": "agent_generated"},
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 2,
         "day_label": "第2天", "title": "学习核心算法", "source": "rule_fallback"},
        {"session_id": session_id, "stage_id": "stage_2", "day_index": 3,
         "day_label": "第3天", "title": "综合复习", "source": "agent_generated"},
    ]
    count = upsert_daily_tasks(db, session_id, tasks)
    assert_true(count == 4, f"Expected 4 tasks inserted, got {count}")
    db.close()
    return session_id


def test_upsert_and_get_daily_tasks() -> None:
    init_db()
    db = SessionLocal()
    session_id = "test_upsert_get_tasks"
    get_or_create_session(db, session_id, learner_id="learner_test", subject_id="math")

    tasks = [
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "Task A", "source": "agent_generated"},
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 2,
         "day_label": "第2天", "title": "Task B", "source": "rule_fallback"},
    ]
    upsert_daily_tasks(db, session_id, tasks)

    # Get all tasks for the session
    all_tasks = get_daily_tasks(db, session_id)
    assert_true(len(all_tasks) == 2, f"Expected 2 tasks, got {len(all_tasks)}")
    assert_true(all_tasks[0].title == "Task A", f"Expected 'Task A', got '{all_tasks[0].title}'")
    assert_true(all_tasks[1].source == "rule_fallback", f"Expected 'rule_fallback', got '{all_tasks[1].source}'")

    # Filter by day
    day1 = get_daily_tasks(db, session_id, day_index=1)
    assert_true(len(day1) == 1, f"Expected 1 task for day 1, got {len(day1)}")
    assert_true(day1[0].title == "Task A", f"Expected 'Task A', got '{day1[0].title}'")

    day3 = get_daily_tasks(db, session_id, day_index=3)
    assert_true(len(day3) == 0, f"Expected 0 tasks for day 3, got {len(day3)}")

    # Re-upsert should replace existing
    new_tasks = [
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "Task C", "source": "agent_generated"},
    ]
    upsert_daily_tasks(db, session_id, new_tasks)
    all_after = get_daily_tasks(db, session_id)
    assert_true(len(all_after) == 1, f"Expected 1 task after re-upsert, got {len(all_after)}")

    db.close()


def test_get_daily_tasks_for_learner() -> None:
    init_db()
    db = SessionLocal()
    learner_id = "test_cross_subject_learner"
    session_a = "test_cs_session_a"
    session_b = "test_cs_session_b"

    get_or_create_session(db, session_a, learner_id=learner_id, subject_id="ai_intro")
    get_or_create_session(db, session_b, learner_id=learner_id, subject_id="ds")

    tasks_a = [
        {"session_id": session_a, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "AI Task 1", "source": "agent_generated"},
    ]
    tasks_b = [
        {"session_id": session_b, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "DS Task 1", "source": "agent_generated"},
        {"session_id": session_b, "stage_id": "stage_1", "day_index": 2,
         "day_label": "第2天", "title": "DS Task 2", "source": "rule_fallback"},
    ]
    upsert_daily_tasks(db, session_a, tasks_a)
    upsert_daily_tasks(db, session_b, tasks_b)

    # Day 1: should have tasks from both sessions
    day1_tasks = get_daily_tasks_for_learner(db, learner_id, day_index=1)
    assert_true(len(day1_tasks) == 2, f"Expected 2 tasks for day 1, got {len(day1_tasks)}")
    titles = {t["title"] for t in day1_tasks}
    assert_true("AI Task 1" in titles, f"Expected 'AI Task 1' in {titles}")
    assert_true("DS Task 1" in titles, f"Expected 'DS Task 1' in {titles}")

    # Day 2: should have only session B's task
    day2_tasks = get_daily_tasks_for_learner(db, learner_id, day_index=2)
    assert_true(len(day2_tasks) == 1, f"Expected 1 task for day 2, got {len(day2_tasks)}")

    # Day 3: should be empty
    day3_tasks = get_daily_tasks_for_learner(db, learner_id, day_index=3)
    assert_true(len(day3_tasks) == 0, f"Expected 0 tasks for day 3, got {len(day3_tasks)}")

    # Verify enrichment fields
    for t in day1_tasks:
        assert_true("sessionId" in t, "Each task should have sessionId")
        assert_true("subjectId" in t, "Each task should have subjectId")
        assert_true("subjectName" in t, "Each task should have subjectName")
        assert_true("completed" in t, "Each task should have completed field")

    db.close()


def test_update_task_completion() -> None:
    init_db()
    session_id = _setup()
    db = SessionLocal()

    tasks = get_daily_tasks(db, session_id)
    assert_true(len(tasks) == 4, f"Expected 4 tasks, got {len(tasks)}")
    task = tasks[0]
    assert_true(task.completed is False, "Task should start as not completed")

    # Mark as completed
    updated = update_task_completion(db, task.id, session_id, completed=True)
    assert_true(updated is not None, "Should return updated task")
    assert_true(updated.completed is True, "Task should now be completed")
    assert_true(updated.completed_at is not None, "completed_at should be set")

    # Un-complete
    updated2 = update_task_completion(db, task.id, session_id, completed=False)
    assert_true(updated2 is not None, "Should return updated task")
    assert_true(updated2.completed is False, "Task should be un-completed")
    assert_true(updated2.completed_at is None, "completed_at should be None")

    # Subject isolation: wrong session_id should return None
    result = update_task_completion(db, task.id, "wrong_session", completed=True)
    assert_true(result is None, "Wrong session_id should return None (subject isolation)")

    db.close()


if __name__ == "__main__":
    test_upsert_and_get_daily_tasks()
    test_get_daily_tasks_for_learner()
    test_update_task_completion()
    print("PASS daily_task_db_test")
