from fastapi import APIRouter,Depends
from course.schema import CourseResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db

router = APIRouter(
    prefix='/student',
    tags=['Student']
)

@router.post("/create-course",response_model=CourseResponse)
async def create_course(data:CourseResponse,db:AsyncSession=Depends(get_db)):
    