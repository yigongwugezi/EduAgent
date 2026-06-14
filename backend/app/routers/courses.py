from fastapi import APIRouter, HTTPException

from app.schemas.common import ApiResponse
from app.services.course_catalog import course_catalog


router = APIRouter(tags=["courses"])


@router.get("/courses")
def list_courses() -> ApiResponse[dict]:
    return ApiResponse(
        data={"courses": course_catalog.list_courses()},
        request_id="req_courses",
    )


@router.get("/courses/{course_id}")
def get_course(course_id: str) -> ApiResponse[dict]:
    course = course_catalog.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return ApiResponse(data={"course": course}, request_id=f"req_course_{course_id}")


@router.get("/courses/{course_id}/chapters/{chapter_id}")
def get_chapter(course_id: str, chapter_id: str) -> ApiResponse[dict]:
    chapter = course_catalog.load_chapter(course_id, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ApiResponse(data={"chapter": chapter}, request_id=f"req_chapter_{course_id}_{chapter_id}")
