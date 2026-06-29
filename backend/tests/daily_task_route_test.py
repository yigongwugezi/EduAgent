"""Test daily task API endpoint functions directly.

Uses the same import pattern as product_routes_test.py to avoid
triggering the RAG optional-dependency import chain.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.engine import SessionLocal, init_db
from app.db.models import SessionModel, LearningPathModel
from app.db.repository import (
    get_or_create_session,
    upsert_daily_tasks,
    upsert_learning_path,
)
from app.routers import product


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _cleanup(session_id: str) -> None:
    db = SessionLocal()
    try:
        session = db.get(SessionModel, session_id)
        if session:
            db.delete(session)
            db.commit()
    finally:
        db.close()


def _setup_session_with_tasks() -> str:
    """Create a session with a learning path and daily tasks."""
    init_db()
    db = SessionLocal()
    session_id = "test_route_daily_session"
    learner_id = "test_route_daily_learner"

    sess = get_or_create_session(db, session_id, learner_id=learner_id, subject_id="ai_intro")

    # Create a learning path
    path_data = {
        "id": f"path_{session_id}_ai_intro",
        "course_id": "ai_intro",
        "course_name": "人工智能导论",
        "description": "测试学习路径",
        "stages": [],
        "overallProgress": 0,
        "estimatedDays": 14,
    }
    upsert_learning_path(db, session_id, path_data)

    # Create daily tasks
    tasks = [
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "学习基础概念", "source": "agent_generated"},
        {"session_id": session_id, "stage_id": "stage_1", "day_index": 1,
         "day_label": "第1天", "title": "完成课后练习", "source": "agent_generated"},
        {"session_id": session_id, "stage_id": "stage_2", "day_index": 2,
         "day_label": "第2天", "title": "学习核心算法", "source": "rule_fallback"},
    ]
    upsert_daily_tasks(db, session_id, tasks)
    db.close()
    return session_id


def test_get_todays_tasks_by_learner() -> None:
    session_id = _setup_session_with_tasks()

    try:
        resp = product.get_todays_daily_tasks(
            learnerId="test_route_daily_learner",
        )
        assert_true(resp["status"] == "success", f"Expected success, got {resp}")
        data = resp["data"]
        assert_true("tasks" in data, "Response should have tasks")
        assert_true("todayDate" in data, "Response should have todayDate")
        assert_true("completedCount" in data, "Response should have completedCount")
        assert_true("totalCount" in data, "Response should have totalCount")

        tasks = data["tasks"]
        for t in tasks:
            assert_true("id" in t, f"Task should have id: {t}")
            assert_true("sessionId" in t, f"Task should have sessionId: {t}")
            assert_true("title" in t, f"Task should have title: {t}")
            assert_true("completed" in t, f"Task should have completed: {t}")
            assert_true("source" in t, f"Task should have source: {t}")
    finally:
        _cleanup(session_id)


def test_get_todays_tasks_by_session() -> None:
    session_id = _setup_session_with_tasks()

    try:
        resp = product.get_todays_daily_tasks(
            sessionId=session_id,
        )
        assert_true(resp["status"] == "success", f"Expected success, got {resp}")
        data = resp["data"]
        assert_true(len(data["tasks"]) >= 1, "Should have tasks for the session")
    finally:
        _cleanup(session_id)


def test_complete_daily_task() -> None:
    session_id = _setup_session_with_tasks()

    try:
        # First get the tasks to find a task ID
        resp = product.get_todays_daily_tasks(learnerId="test_route_daily_learner")
        tasks = resp["data"]["tasks"]
        assert_true(len(tasks) >= 1, "Should have at least 1 task")

        task = tasks[0]
        task_id = task["id"]

        # Toggle to completed
        resp2 = product.complete_daily_task(task_id, {
            "sessionId": session_id,
            "completed": True,
        })
        assert_true(resp2["status"] == "success", f"Expected success, got {resp2}")
        assert_true(resp2["data"]["ok"] is True, f"Expected ok=True, got {resp2['data']}")
        assert_true(resp2["data"]["task"]["completed"] is True,
                    f"Task should be completed: {resp2['data']['task']}")

        # Toggle back to not completed
        resp3 = product.complete_daily_task(task_id, {
            "sessionId": session_id,
            "completed": False,
        })
        assert_true(resp3["data"]["ok"] is True, f"Expected ok=True, got {resp3['data']}")
        assert_true(resp3["data"]["task"]["completed"] is False,
                    f"Task should NOT be completed: {resp3['data']['task']}")
    finally:
        _cleanup(session_id)


def test_complete_task_wrong_session_returns_404() -> None:
    session_id = _setup_session_with_tasks()

    # Create a second session that also exists
    db = SessionLocal()
    from app.db.repository import get_or_create_session as _goc
    wrong_session_id = "test_route_wrong_session"
    _goc(db, wrong_session_id, learner_id="test_route_daily_learner", subject_id="other")
    db.close()

    try:
        resp = product.get_todays_daily_tasks(learnerId="test_route_daily_learner")
        tasks = resp["data"]["tasks"]
        task_id = tasks[0]["id"]

        # Attempt to complete with a different but valid sessionId
        from app.utils.errors import NotFoundError
        raised = False
        try:
            product.complete_daily_task(task_id, {
                "sessionId": wrong_session_id,
                "completed": True,
            })
        except NotFoundError:
            raised = True
        assert_true(raised, "Should raise NotFoundError for wrong sessionId (subject isolation)")
    finally:
        _cleanup(session_id)
        _cleanup(wrong_session_id)


def test_get_session_daily_tasks() -> None:
    session_id = _setup_session_with_tasks()

    try:
        resp = product.get_session_daily_tasks(
            session_id,
            sessionId=session_id,
        )
        assert_true(resp["status"] == "success", f"Expected success, got {resp}")
        data = resp["data"]
        assert_true("tasks" in data, "Response should have tasks")
        assert_true("dayCount" in data, "Response should have dayCount")
        assert_true("currentDay" in data, "Response should have currentDay")
        assert_true(data["dayCount"] == 14, f"Expected 14 days, got {data['dayCount']}")
        assert_true(data["currentDay"] >= 1, "currentDay should be >= 1")

        # Filter by day 2
        resp2 = product.get_session_daily_tasks(
            session_id,
            sessionId=session_id,
            day=2,
        )
        data2 = resp2["data"]
        for t in data2["tasks"]:
            assert_true(t["dayIndex"] == 2, f"Task dayIndex should be 2: {t}")
    finally:
        _cleanup(session_id)


def test_get_session_daily_tasks_no_path_returns_empty() -> None:
    resp = product.get_session_daily_tasks(
        "nonexistent_session_test",
        sessionId="nonexistent_session_test",
    )
    assert_true(resp["status"] == "success", f"Expected success, got {resp}")
    data = resp["data"]
    assert_true(len(data["tasks"]) == 0, "Should have 0 tasks for nonexistent session")


def test_compute_current_day() -> None:
    """Test the _compute_current_day helper."""
    from datetime import datetime, timezone, timedelta

    # No created_at -> day 1
    assert_true(product._compute_current_day(None, 14) == 1, "None created_at should default to day 1")

    # Created just now -> day 1
    now = datetime.now(timezone.utc)
    assert_true(product._compute_current_day(now, 14) == 1, "Just-created path should be day 1")

    # Created yesterday -> day 2
    yesterday = now - timedelta(days=1)
    assert_true(product._compute_current_day(yesterday, 14) == 2, "Yesterday-created path should be day 2")

    # Created 30 days ago but max is 14 -> day 14 (cap)
    long_ago = now - timedelta(days=30)
    assert_true(product._compute_current_day(long_ago, 14) == 14, "Old path should cap at max_days")

    # Created 30 days ago, max 365 -> day 31
    assert_true(product._compute_current_day(long_ago, 365) == 31, "Old path with large max")


def test_task_to_dict() -> None:
    """Test the _task_to_dict helper."""
    from app.db.models import DailyTaskModel, SessionModel

    task = DailyTaskModel(
        id=42,
        session_id="sess_1",
        stage_id="stage_1",
        day_index=3,
        day_label="第3天",
        title="Test Task",
        description="A test task",
        source="agent_generated",
    )
    sess = SessionModel(
        id="sess_1",
        subject_id="ai_intro",
        title="AI导论",
    )

    result = product._task_to_dict(task, sess)
    assert_true(result["id"] == 42, f"Expected id 42, got {result['id']}")
    assert_true(result["sessionId"] == "sess_1", f"Expected sessionId sess_1, got {result['sessionId']}")
    assert_true(result["subjectId"] == "ai_intro", f"Expected subjectId ai_intro, got {result['subjectId']}")
    assert_true(result["subjectName"] == "AI导论", f"Expected subjectName AI导论, got {result['subjectName']}")
    assert_true(result["title"] == "Test Task", f"Expected title 'Test Task', got {result['title']}")
    assert_true(result["completed"] is False, "Should default to not completed")
    assert_true(result["source"] == "agent_generated", f"Expected source agent_generated, got {result['source']}")


if __name__ == "__main__":
    test_get_todays_tasks_by_learner()
    test_get_todays_tasks_by_session()
    test_complete_daily_task()
    test_complete_task_wrong_session_returns_404()
    test_get_session_daily_tasks()
    test_get_session_daily_tasks_no_path_returns_empty()
    test_compute_current_day()
    test_task_to_dict()
    print("PASS daily_task_route_test")
