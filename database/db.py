from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy.orm import DeclarativeBase

BASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    BASE_URL,
    echo=True
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session

