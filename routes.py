# routes.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

import bcrypt

from database import get_db
import models, schemas
from models import User, Task, AuditLog
from auth import verify_password, create_access_token, get_current_user
from crud import get_user_by_email, create_password_reset_token, send_reset_email
from utils import log_audit_action
from dependencies import RoleChecker

router = APIRouter()


class PauseReason(BaseModel):
    reason: str


# ── Dashboards ───────────────────────────────────────────────────────────────
@router.get("/admin/dashboard", dependencies=[Depends(RoleChecker(["admin"]))])
async def admin_dashboard():
    return {"message": "Welcome to the Admin Dashboard"}


@router.get(
    "/admin/logs",
    dependencies=[Depends(RoleChecker(["admin"]))],
    response_model=list[schemas.Message],
)
async def get_audit_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
    return [
        schemas.Message(
            message=f"{log.timestamp} – User {log.user_id} {log.action} {log.target}"
        )
        for log in result.scalars().all()
    ]


@router.get(
    "/manager/dashboard", dependencies=[Depends(RoleChecker(["admin", "manager"]))]
)
async def manager_dashboard():
    return {"message": "Welcome to the Manager Dashboard"}


# ── Auth ─────────────────────────────────────────────────────────────────────
@router.post(
    "/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED
)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(User).filter_by(email=user_in.email))
    if r.scalars().first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    hashed = bcrypt.hashpw(user_in.password.encode(), bcrypt.gensalt()).decode()
    u = User(email=user_in.email, hashed_password=hashed)
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    r = await db.execute(select(User).where(User.email == form_data.username))
    user = r.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=schemas.Message)
async def forgot_password(
    payload: schemas.ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    token = await create_password_reset_token(db, user.id)
    background_tasks.add_task(send_reset_email, user.email, token)
    return {"message": "If that email exists, a reset link has been sent."}


# ── Task Management ────────────────────────────────────────────────────────────


# Create (admin & manager only)
@router.post(
    "/tasks",
    response_model=schemas.TaskOut,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def create_task(
    payload: schemas.TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = Task(
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
        due_date=payload.due_date,
        recurrence=payload.recurrence,
        recurrence_end=payload.recurrence_end,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    await log_audit_action(current_user.id, "Created Task", t.title, db)
    return schemas.TaskOut.from_orm(t)


# Read (everyone sees only `status='active'`)
@router.get("/tasks", response_model=list[schemas.TaskOut])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    due: Optional[str] = Query(None, regex="^(overdue|today|upcoming)$"),
):
    q = select(Task).where(Task.status == "active")
    now = datetime.utcnow()
    if due == "overdue":
        q = q.where(Task.due_date < now, Task.is_complete == False)
    elif due == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        q = q.where(Task.due_date >= start, Task.due_date < start + timedelta(days=1))
    elif due == "upcoming":
        q = q.where(Task.due_date > now)
    res = await db.execute(q)
    return [schemas.TaskOut.from_orm(t) for t in res.scalars().all()]


# Update (admin & manager only)
@router.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut,
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def update_task(
    task_id: int,
    upd: schemas.TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.title = upd.title
    t.description = upd.description
    await db.commit()
    await db.refresh(t)
    await log_audit_action(current_user.id, "Edited Task", f"#{task_id}", db)
    return t


# Delete (admin only)
@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    await db.delete(t)
    await db.commit()
    await log_audit_action(current_user.id, "Deleted Task", f"#{task_id}", db)


# ── User actions ───────────────────────────────────────────────────────────────


@router.patch("/tasks/{task_id}/start", response_model=schemas.TaskOut)
async def start_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.start_time = datetime.utcnow()
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/tasks/{task_id}/pause", response_model=schemas.TaskOut)
async def pause_task(
    task_id: int,
    payload: PauseReason,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.paused_at = datetime.utcnow()
    t.pause_reason = payload.reason
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/tasks/{task_id}/resume", response_model=schemas.TaskOut)
async def resume_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.resumed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/tasks/{task_id}/complete", response_model=schemas.TaskOut)
async def toggle_complete(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.is_complete = not t.is_complete
    t.completed_at = datetime.utcnow() if t.is_complete else None
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/tasks/{task_id}/end", response_model=schemas.TaskOut)
async def end_for_approval(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t or t.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    t.end_time = datetime.utcnow()
    t.status = "pending_approval"
    await db.commit()
    await db.refresh(t)
    await log_audit_action(current_user.id, "Ended (pending)", f"#{task_id}", db)
    return t


@router.get(
    "/tasks/pending",
    response_model=list[schemas.TaskOut],
    dependencies=[Depends(RoleChecker(["manager", "admin"]))],
)
async def pending(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Task).where(Task.status == "pending_approval"))
    return [schemas.TaskOut.from_orm(t) for t in r.scalars().all()]


@router.patch(
    "/tasks/{task_id}/approve",
    response_model=schemas.TaskOut,
    dependencies=[Depends(RoleChecker(["manager", "admin"]))],
)
async def approve(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t or t.status != "pending_approval":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No pending task")
    t.status = "approved"
    await db.commit()
    await db.refresh(t)
    await log_audit_action(current_user.id, "Approved Task", f"#{task_id}", db)
    return t


@router.patch(
    "/tasks/{task_id}/reject",
    response_model=schemas.TaskOut,
    dependencies=[Depends(RoleChecker(["manager", "admin"]))],
)
async def reject(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t = await db.get(Task, task_id)
    if not t or t.status != "pending_approval":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No pending task")
    t.status = "active"
    t.end_time = None
    await db.commit()
    await db.refresh(t)
    await log_audit_action(current_user.id, "Rejected Task", f"#{task_id}", db)
    return t
