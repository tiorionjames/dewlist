from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from server.database import get_db
from server.models import Task, User
from server.schemas import TaskOut
from server.utils.task_helpers import get_task, record_task_history

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# List all tasks (demo)
@router.get("/", response_model=List[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


# Start task
@router.post("/{task_id}/start")
def start_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if task.assigned_to != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if task.status not in ["New", "Paused"]:
        raise HTTPException(
            status_code=400, detail="Cannot start task in current status"
        )
    return record_task_history(db, task, "In Progress", user_id, "User started task")


# Pause task
@router.post("/{task_id}/pause")
def pause_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if task.assigned_to != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if task.status != "In Progress":
        raise HTTPException(status_code=400, detail="Can only pause tasks in progress")
    return record_task_history(db, task, "Paused", user_id, "User paused task")


# Resume task
@router.post("/{task_id}/resume")
def resume_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if task.assigned_to != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if task.status != "Paused":
        raise HTTPException(status_code=400, detail="Can only resume paused tasks")
    return record_task_history(db, task, "In Progress", user_id, "User resumed task")
