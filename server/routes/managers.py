# server/routes/managers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import Task, User
from server.utils.task_helpers import get_task, record_task_history

router = APIRouter(prefix="/manager", tags=["Manager"])


@router.post("/tasks/{task_id}/approve")
def approve_task(task_id: int, manager_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    manager = db.query(User).filter(User.user_id == manager_id).first()
    if not manager or manager.role not in ["Manager", "Admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if task.status != "Needs Review":
        raise HTTPException(status_code=400, detail="Task not pending review")
    return record_task_history(
        db, task, "Approved", manager_id, "Manager approved task"
    )


@router.post("/tasks/{task_id}/reopen")
def reopen_task(
    task_id: int, manager_id: int, user_id: int, db: Session = Depends(get_db)
):
    task = get_task(db, task_id)
    manager = db.query(User).filter(User.user_id == manager_id).first()
    if not manager or manager.role not in ["Manager", "Admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    task.assigned_to = user_id
    return record_task_history(
        db, task, "In Progress", manager_id, "Task reopened and reassigned to user"
    )
