from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import HOST, PORT
from database.db import engine, Base
import student.model
import course.model
from schemas import AnalyzeRequest, Task
from services import analyze_student_history, parse_csv_tasks
from student.router import router as student_router


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


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Academic Procrastination Detection API is running",
    }


@app.post("/analyze")
@app.post("/classify")
def analyze(payload: Union[AnalyzeRequest, list[Task]]):
    user_id = None
    tasks: list[Task] = []

    if isinstance(payload, list):
        tasks = payload
    else:
        user_id = payload.user_id
        if payload.csv_data:
            tasks = parse_csv_tasks(payload.csv_data)
        elif payload.tasks:
            tasks = payload.tasks

    if not tasks:
        raise HTTPException(
            status_code=400,
            detail="Send a list of tasks or csv_data.",
        )

    return analyze_student_history(tasks=tasks, user_id=user_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
