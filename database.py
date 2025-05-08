from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "mysql+aiomysql://dewuser:secret_pw@db:3306/dewlist"


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


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


SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
