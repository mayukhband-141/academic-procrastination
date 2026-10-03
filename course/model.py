from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import ForeignKey
from database.db import Base
from typing import List, TYPE_CHECKING
from datetime import datetime
if TYPE_CHECKING:
    from student.model import Student

class Course(Base):
    __tablename__= "courses"
    id:Mapped[int] = mapped_column(primary_key=True)
    subject:Mapped[str] = mapped_column(nullable=False)
    assigned: Mapped[int] = mapped_column(ForeignKey("student_details.id"))
    assigned_at:Mapped[datetime] = mapped_column(default=datetime.now())
    submitted:Mapped[datetime] = mapped_column(nullable=False)
    reschedules:Mapped[int] = mapped_column(default=0)
