from fastapi import APIRouter,HTTPException
from models.schemas import AnalyzeRequest, Task
from typing import Union
from models.services import analyze_student_history, parse_csv_tasks

router = APIRouter()

@router.post("/analyze")
@router.post("/classify")
@router.post("/model/analyze")
@router.post("/model/classify")
def analyze(payload: Union[AnalyzeRequest, list[Task]]):
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

    if not tasks:
        raise HTTPException(
            status_code=400,
            detail="Send a list of tasks or csv_data.",
        )

    return analyze_student_history(tasks=tasks, user_id=user_id)
