from fastapi import APIRouter,Depends,HTTPException
from course.schema import CourseRequest, CourseResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from sqlalchemy import select
from student.model import Student
from .model import Course

router = APIRouter()

@router.post("/create-course", response_model=CourseResponse)
async def create_course(user_id: int, data: CourseRequest, db: AsyncSession = Depends(get_db)):
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="User data required"
        )
    res = await db.execute(select(Student).where(Student.id == user_id))
    student = res.scalar_one_or_none()
    if student is None:
        all_st = await db.execute(select(Student))
        student = all_st.scalars().first()
        if student is None:
            student = Student(fullname="Demo Student", email="demo@university.edu")
            db.add(student)
            await db.commit()
            await db.refresh(student)
    course = Course(
        subject=data.subject,
        assigned=data.user_id,
        assigned_at=data.assigned_at,
        submitted = data.submitted,
        due_date=data.due,
        reschedules= data.reschedules
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    await db.refresh(student)
    return course

@router.post("/update-course",response_model=CourseResponse)
async def update_course(user_id:int,data:CourseResponse,db:AsyncSession=Depends(get_db)):
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="User data required"
        )
    res = await db.execute(
        select(Student).where(Student.id==user_id)
    )
    student = res.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    course = Course(
        subject=data.subject,
        assigned=data.user_id,
        assigned_at=data.assigned_at,
        submitted = data.submitted,
        due_date=data.due,
        reschedules= data.reschedules
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    await db.refresh(student)
    return course


