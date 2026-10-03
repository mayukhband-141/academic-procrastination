from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import ForeignKey
from database.db import Base
from typing import List
from datetime import datetime,timedelta
from course.model import Course
from student.model import Student

class Course(Base):
    __tablename__= "courses"
    id:Mapped[int] = mapped_column(primary_key=True)
    subject:Mapped[str] = mapped_column(nullable=False)
    assigned: Mapped[int] = mapped_column(ForeignKey("student_details.id"))
    assigned_at:Mapped[datetime] = mapped_column(default=datetime.now())
    due_date:Mapped[datetime] = mapped_column(default=datetime.now()+timedelta(days=7))
    submitted:Mapped[datetime] = mapped_column(nullable=False)
    reschedules:Mapped[int] = mapped_column(default=0)
