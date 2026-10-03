from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime

class CourseResponse(BaseModel):
    user_id: int
    subject: str
    assigned_at:datetime
    due:datetime
    submitted:datetime
    reschedules:int

class UpdateSchedules(BaseModel):
    user_id: int
    subject: str
    assigned_at:datetime
    due:datetime
    submitted:datetime
    reschedules:int