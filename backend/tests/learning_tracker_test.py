import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.learning_tracker import LearningTracker  # noqa: E402


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> None:
    tracker = LearningTracker()
    tracker.log({"event": "resource_view", "resourceId": "res_lecture_001", "duration": 20}, session_id="s1")
    tracker.log(
        {
            "event": "quiz_result",
            "resourceId": "res_quiz_001",
            "duration": 15,
            "metadata": {"topic": "stack", "correct": 3, "total": 5, "wrong": 2},
        },
        session_id="s1",
    )
    tracker.log({"event": "resource_view", "resourceId": "res_other", "duration": 99}, session_id="s2")

    summary = tracker.summary("s1")
    assert_equal(summary["eventCount"], 2, "eventCount")
    assert_equal(summary["totalStudyMinutes"], 35, "totalStudyMinutes")
    assert_equal(summary["activeResourceCount"], 2, "activeResourceCount")
    assert_equal(summary["quizAccuracy"], 60, "quizAccuracy")
    assert_equal(summary["weakTopics"][0]["topic"], "stack", "weak topic")
    assert_true(summary["recommendations"], "recommendations should not be empty")

    tracker.reset("s1")
    assert_equal(tracker.summary("s1")["eventCount"], 0, "reset only s1")
    assert_equal(tracker.summary("s2")["eventCount"], 1, "s2 remains")
    print("PASS learning_tracker_test")


if __name__ == "__main__":
    main()
