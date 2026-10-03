from sqlalchemy.orm import mapped_column,Mapped,relationship
from sqlalchemy import ForeignKey
from database.db import Base
from typing import List
from datetime import datetime
from course.model import Course

class Student(Base):
    __tablename__= "student_details"
    id:Mapped[int] = mapped_column(primary_key=True)
    fullname:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(unique=True,nullable=False)
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="student", cascade="all, delete-orphan")
    due: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)