from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.db import get_db
from student.model import Student
from student.schema import StudentRequest, StudentResponse

router = APIRouter()

@router.post("/", response_model=StudentResponse)
@router.post("/create")
async def create_student(payload: StudentRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Student).where(Student.email == payload.email))
    existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this email already exists")

    student = Student(
        fullname=payload.fullname,
        email=payload.email
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student

@router.get("/{student_id}")
async def get_student_info(student_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Student).where(Student.id == student_id))
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
@router.get("/")
async def list_students(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Student))
    students = res.scalars().all()
    return [
        {
            "id": s.id,
            "name": s.fullname,
            "email": s.email,
            "due": s.due,
            "created_at": s.created_at
        }
        for s in students
    ]
