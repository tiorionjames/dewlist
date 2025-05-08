# /app/schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# User schemas


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    role: str

    # Enable ORM mode for SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Auth schemas


class Token(BaseModel):
    access_token: str
    token_type: str


# ─────────────────────────────────────────────────────────────────────────────
# Task schemas


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    recurrence_end: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    user_id: int
    is_complete: bool
    completed_at: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    pause_reason: Optional[str] = None
    resumed_at: Optional[datetime] = None
    recurrence_label: Optional[str] = None

    # Enable ORM mode for SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────────────────────
# Forgot password flow


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class Message(BaseModel):
    message: str  # for simple responses
