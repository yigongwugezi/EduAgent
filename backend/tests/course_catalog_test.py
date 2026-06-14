import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.course_catalog import CourseCatalog  # noqa: E402
from app.routers import product  # noqa: E402
from app.services.conversation_state import conversation_store  # noqa: E402


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(label)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    catalog = CourseCatalog(ROOT.parent / "knowledge_base" / "courses")
    courses = catalog.list_courses()
    ids = {course["course_id"] for course in courses}
    assert_true("ai_intro" in ids, "ai_intro should be discoverable")
    assert_true("data_structures" in ids, "data_structures should be discoverable")

    data_structures = catalog.get_course("data_structures")
    assert_true(data_structures is not None, "data_structures detail should load")
    assert_equal(data_structures["chapter_count"], 6, "data_structures chapter_count")
    assert_true("数据结构" in data_structures["outline"], "outline should be loaded")

    chapter = catalog.load_chapter("data_structures", "03")
    assert_true(chapter is not None, "chapter 03 should load")
    assert_true("栈" in chapter["content"], "chapter content should include stack")

    assert_equal(catalog.match_course("数据结构")["course_id"], "data_structures", "match 数据结构")
    assert_equal(catalog.match_course("我想复习栈和队列")["course_id"], "data_structures", "match stack queue")

    session_id = "course_selection_test"
    conversation_store.reset(session_id)
    conversation_store.append_message(session_id, "user", "我是软件工程大二学生，想学习数据结构，为了考试通过")
    result = product._run_agents("开始生成学习方案", session_id=session_id)
    assert_equal(result["course_id"], "data_structures", "agent run course_id")
    assert_equal(result["course"]["course_name"], "数据结构", "agent run course name")
    print("PASS course_catalog_test")


if __name__ == "__main__":
    main()
