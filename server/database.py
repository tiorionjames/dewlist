# server/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dewuser:dewpass@localhost:5432/dewlist"
)

# future=True for 2.0 style / pool_pre_ping to avoid stale connections
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
