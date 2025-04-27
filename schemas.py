from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


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
    completed_at: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    paused_at: Optional[datetime]
    pause_reason: Optional[str]
    resumed_at: Optional[datetime]
    recurrence_label: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    detail: str
