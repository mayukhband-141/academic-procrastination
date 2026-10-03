from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import HOST, PORT
from database.db import engine, Base
import student.model
import course.model
from student.router import router as student_router
from course.router import router as course_router
from models.router import router as model_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
app = FastAPI(title="Academic Procrastination Detection API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(student_router, prefix="/students", tags=["students"])
app.include_router(course_router, prefix="/courses", tags=["courses"])
app.include_router(model_router, tags=["models"])


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Academic Procrastination Detection API is running",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
