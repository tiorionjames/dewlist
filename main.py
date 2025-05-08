# main.py

import os
import asyncio
import aiomysql
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_engine, get_engine
from models import Base
from routes import router

app = FastAPI()

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] while debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def wait_for_mysql(
    host: str,
    port: int,
    user: str,
    password: str,
    db: str,
    retries: int = 20,
    delay: float = 1.0,
):
    for attempt in range(retries):
        try:
            conn = await aiomysql.connect(
                host=host, port=port, user=user, password=password, db=db
            )
            conn.close()
            print("✅ MySQL is ready!")
            return
        except Exception:
            await asyncio.sleep(delay)
    raise RuntimeError("Could not connect to MySQL")


@app.on_event("startup")
async def on_startup():
    init_engine(os.getenv("DATABASE_URL"))
    await wait_for_mysql("db", 3306, "dewuser", "secret_pw", "dewlist")
    engine = get_engine()
    async with engine.begin() as conn:
        # This only CREATEs missing tables—it won’t ALTER existing ones!
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created (if they weren’t already)")


app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Welcome to DewList!"}
