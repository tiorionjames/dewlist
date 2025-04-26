import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from database import init_engine, get_engine
from routes import router
import models


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup():
        init_engine(os.getenv("DATABASE_URL"))
        await initialize_database()

    app.include_router(router)

    @app.get("/")
    def read_root():
        return {"message": "Welcome to DewList!"}

    return app


async def wait_for_postgres():
    import asyncpg

    for i in range(20):
        try:
            conn = await asyncpg.connect(
                user="postgres",
                password="postgres",
                database="dewlist",
                host="db",
                port=5432,
            )
            await conn.close()
            print(f"✅ Postgres TCP connection successful at attempt {i+1}")
            return
        except (asyncpg.exceptions.CannotConnectNowError, ConnectionRefusedError) as e:
            print(f"⏳ TCP connection not ready, retry {i+1}/20… ({e})")
            await asyncio.sleep(2)
    raise RuntimeError(
        "🚨 Could not establish TCP connection to Postgres after 20 attempts."
    )


async def initialize_database():
    await wait_for_postgres()

    print("😴 Sleeping for 5 seconds to let Postgres fully wake up...")
    await asyncio.sleep(5)

    engine = get_engine()
    if engine is None:
        raise RuntimeError("🚨 Engine is still None when trying to create tables!")

    for i in range(20):
        try:
            print(f"🔨 Trying to create database schema (attempt {i+1})...")
            async with engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.create_all)
            print(f"✅ Database schema created successfully at attempt {i+1}")
            return
        except OperationalError as e:
            print(f"⏳ Database schema not ready, retry {i+1}/20… ({e})")
            await asyncio.sleep(2)
    raise RuntimeError("🚨 Could not initialize database schema after 20 attempts.")


app = create_app()
