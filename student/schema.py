from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from course.schema import CourseResponse
from typing import List
class StudentRequest(BaseModel):
    fullname: str = Field(min_length=5,max_length=30)
    email:str = Field(min_length=7)

class StudentResponse(StudentRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at : datetime

class StudentCourses(StudentResponse):
    model_config = ConfigDict(from_attributes=True)
    courses:CourseResponse
    course_id: List[int]
