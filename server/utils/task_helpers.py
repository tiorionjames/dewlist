# server/utils/task_helpers.py
from sqlalchemy.orm import Session
from server.models import Task, TaskHistory
from datetime import datetime
from fastapi import HTTPException, status


def get_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


def record_task_history(
    db: Session, task: Task, new_status: str, user_id: int, note: str
):
    history = TaskHistory(
        task_id=task.task_id,
        previous_status=task.status,
        new_status=new_status,
        changed_by=user_id,
        changed_at=datetime.utcnow(),
        note=note,
    )
    db.add(history)
    task.status = new_status
    task.updated_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB commit failed"
        )
    return task
