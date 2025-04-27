from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import Optional
from utils import strip_timezone
from utils import sanitize_datetime_fields
from pydantic import BaseModel
from models import User

import models, schemas
from database import get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    create_reset_token,
    verify_reset_token,
)

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/tasks", response_model=schemas.TaskOut)
async def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sanitized_task_data = sanitize_datetime_fields(task.dict())
    new_task = models.Task(**sanitized_task_data, user_id=current_user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    task_out = schemas.TaskOut.from_orm(new_task)

    def build_label(task):
        if task.recurrence and task.recurrence_end:
            return f"Repeats {task.recurrence} until {task.recurrence_end.date()}"
        elif task.recurrence:
            return f"Repeats {task.recurrence}"
        return None

    task_out.recurrence_label = build_label(new_task)

    return task_out


@router.get("/tasks", response_model=list[schemas.TaskOut])
async def get_tasks(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    due: Optional[str] = Query(None, regex="^(overdue|today|upcoming)$"),
):
    query = select(models.Task).where(models.Task.user_id == current_user.id)
    now = datetime.utcnow()
    if due == "overdue":
        query = query.where(
            models.Task.due_date < now, models.Task.is_complete == False
        )
    elif due == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        query = query.where(models.Task.due_date >= start, models.Task.due_date < end)
    elif due == "upcoming":
        query = query.where(models.Task.due_date > now)
    result = await db.execute(query)
    tasks = result.scalars().all()

    def build_label(task):
        if task.recurrence and task.recurrence_end:
            return f"Repeats {task.recurrence} until {task.recurrence_end.date()}"
        elif task.recurrence:
            return f"Repeats {task.recurrence}"
        return None

    return [
        schemas.TaskOut(**task.__dict__, recurrence_label=build_label(task))
        for task in tasks
    ]


@router.put("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(
    task_id: int,
    updated_task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/complete", response_model=schemas.TaskOut)
async def toggle_complete(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.is_complete:
        task.is_complete = False
        task.completed_at = None
    else:
        task.is_complete = True
        task.completed_at = datetime.utcnow()
        if task.recurrence and task.due_date:
            delta_map = {
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1),
                "monthly": timedelta(days=30),
                "yearly": timedelta(days=365),
            }
            next_delta = delta_map.get(task.recurrence)
            if next_delta:
                next_due = task.due_date + next_delta
                if not task.recurrence_end or next_due <= task.recurrence_end:
                    new_task = models.Task(
                        title=task.title,
                        description=task.description,
                        due_date=next_due,
                        recurrence=task.recurrence,
                        recurrence_end=task.recurrence_end,
                        user_id=current_user.id,
                    )
                    db.add(new_task)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.patch("/tasks/{task_id}/start", response_model=schemas.TaskOut)
async def start_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.start_time = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/end", response_model=schemas.TaskOut)
async def end_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await db.get(models.Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.end_time = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task


class PauseReason(BaseModel):
    reason: str


@router.patch("/tasks/{task_id}/pause", response_model=schemas.TaskOut)
async def pause_task(
    task_id: int,
    reason: PauseReason,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await db.get(models.Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.paused_at = datetime.utcnow()
    task.pause_reason = reason.reason
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/resume", response_model=schemas.TaskOut)
async def resume_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await db.get(models.Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.resumed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task
