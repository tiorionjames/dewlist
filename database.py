from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://<user>:<pass>@localhost/<dbname>"


engine: Optional[AsyncSession] = None
AsyncSessionLocal: Optional[sessionmaker] = None


def get_engine():
    return engine


def init_engine(database_url: str):
    global engine, AsyncSessionLocal
    print(f"🚀 INIT_ENGINE called with URL: {database_url}")
    engine = create_async_engine(database_url, echo=True)
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    print(f"✅ Engine and SessionLocal created!")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
