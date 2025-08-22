from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# --- Users ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "User"


class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True


# --- Tasks ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None


class TaskOut(BaseModel):
    task_id: int
    title: str
    description: Optional[str]
    status: str
    assigned_to: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
