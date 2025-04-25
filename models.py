from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_complete = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    recurrence = Column(String, nullable=True)
    recurrence_end = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    pause_reason = Column(String, nullable=True)
    resumed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="tasks")
