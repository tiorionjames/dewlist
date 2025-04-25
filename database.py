from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# For SQLite (zero-config). To use Postgres, swap the URL accordingly:
DATABASE_URL = "postgresql+asyncpg://<user>:<pass>@localhost/<dbname>"
# DATABASE_URL = "sqlite+aiosqlite:///./dewlist.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
