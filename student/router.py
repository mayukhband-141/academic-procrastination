from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.db import get_db
from student.model import Student
from student.schema import StudentRequest, StudentResponse

router = APIRouter()

# create student
@router.post("/", response_model=StudentResponse)
@router.post("/create")
async def create_student(payload: StudentRequest, db: AsyncSession = Depends(get_db)):
    # check if email exists
    q = select(Student).where(Student.email == payload.email)
    res = await db.execute(q)
    existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this email already exists")

    new_student = Student(
        fullname=payload.name,
        email=payload.email
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    return {
        "id": new_student.id,
        "name": new_student.fullname,
        "email": new_student.email,
        "created_at": new_student.created_at
    }


# get student details
@router.get("/{student_id}")
async def get_student_info(student_id: int, db: AsyncSession = Depends(get_db)):
    q = select(Student).where(Student.id == student_id)
    res = await db.execute(q)
    student = res.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student.id,
        "name": student.fullname,
        "email": student.email,
        "due": student.due,
        "created_at": student.created_at
    }


@router.get("/")
async def list_students(db: AsyncSession = Depends(get_db)):
    # just dump all students
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
