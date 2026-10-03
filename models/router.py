from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db
from course.model import Course
from models.schemas import AnalyzeRequest, Task
from typing import Union
from models.services import analyze_student_history, parse_csv_tasks

router = APIRouter()

@router.post("/analyze")
@router.post("/classify")
@router.post("/model/analyze")
@router.post("/model/classify")
async def analyze(payload: Union[AnalyzeRequest, list[Task]], db: AsyncSession = Depends(get_db)):
    user_id = None
    tasks: list[Task] = []

    if isinstance(payload, list):
        tasks = payload
    else:
        user_id = payload.user_id
        if payload.csv_data:
            tasks = parse_csv_tasks(payload.csv_data)
        elif payload.tasks:
            tasks = payload.tasks

    # If user_id is provided and no tasks were passed in body, fetch student courses from Database!
    if user_id is not None and not tasks:
        res = await db.execute(select(Course).where(Course.assigned == user_id))
        db_courses = res.scalars().all()
        for c in db_courses:
            tasks.append(Task(
                task_id=f"C-{c.id}",
                course=c.subject,
                assigned=c.assigned_at.isoformat() if c.assigned_at else "",
                due=c.due_date.isoformat() if c.due_date else "",
                submitted=c.submitted.isoformat() if c.submitted else None,
                reschedules=c.reschedules or 0
            ))

    if not tasks:
        if user_id is not None:
            return {
                "user_id": user_id,
                "label": "none",
                "onset_task": None,
                "scores": [],
                "explanation": "No assignment history found yet.",
            }
        raise HTTPException(
            status_code=400,
            detail="Send a list of tasks or csv_data.",
        )

    return analyze_student_history(tasks=tasks, user_id=user_id)
