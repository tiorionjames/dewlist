# server/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    tasks_created = relationship(
        "Task", back_populates="creator", foreign_keys="Task.created_by"
    )
    tasks_assigned = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to"
    )


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(64), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="New")
    assigned_to = Column(Integer, ForeignKey("users.user_id"))
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = relationship(
        "User", foreign_keys=[assigned_to], back_populates="tasks_assigned"
    )
    creator = relationship(
        "User", foreign_keys=[created_by], back_populates="tasks_created"
    )
    history = relationship(
        "TaskHistory", back_populates="task", cascade="all, delete-orphan"
    )


class TaskHistory(Base):
    __tablename__ = "task_history"

    history_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    previous_status = Column(String(20))
    new_status = Column(String(20))
    changed_by = Column(Integer, ForeignKey("users.user_id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)

    task = relationship("Task", back_populates="history")
