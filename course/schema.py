from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CourseRequest(BaseModel):
    user_id: int
    subject: str
    assigned_at: datetime
    due: datetime
    submitted: datetime | None = None
    reschedules: int = 0
class CourseResponse(CourseRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
class UpdateSchedules(BaseModel):
    user_id: int
    subject: str
    assigned_at: datetime
    due: datetime
    submitted: datetime | None = None
    reschedules: int = 0