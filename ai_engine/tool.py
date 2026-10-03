from course.model import Course
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from student.model import Student
from fastapi import HTTPException

async def get_score(userid:int,db:AsyncSession):
    result = await db.execute(
        select(Student).where(userid == Student.id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return HTTPException(
            status_code=404,
            detail="user not found"
        )
    course_res = await db.execute(
        select(Course).where(Course.assigned == userid)
    )
    courses = course_res.scalars().all()
    return courses

