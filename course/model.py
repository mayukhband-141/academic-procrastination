from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import ForeignKey
from database.db import Base
from typing import List
from datetime import datetime
from course.model import Course
from student.model import Student

class Course(Base):
    __tablename__= "courses"
    id:Mapped[int] = mapped_column(primary_key=True)
    subject:Mapped[str] = mapped_column(nullable=False)
    assigned:Mapped["Student"] = mapped_column(ForeignKey("students.id"))
    assigned_at:Mapped[datetime] = mapped_column(default=datetime.now())
    submitted:Mapped[datetime] = mapped_column(nullable=False)
    reschedules:Mapped[int] = mapped_column(default=0)
