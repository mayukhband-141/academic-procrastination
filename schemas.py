from pydantic import BaseModel

class Task(BaseModel):
    task_id: str
    course: str
    assigned: str
    due: str
    first_activity: str | None = None
    submitted: str | None = None
    reschedules: int | None = 0

class AnalyzeRequest(BaseModel):
    user_id: int | None = None
    tasks: list[Task] = []
    csv_data: str | None = None
