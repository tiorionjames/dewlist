# server/crud.py
from sqlalchemy.orm import Session
from server.models import Task, TaskHistory
from datetime import datetime
from fastapi import HTTPException, status


def complete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    # Only allow users to complete tasks assigned to them
    if task.assigned_to != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )

    # Record history
    history = TaskHistory(
        task_id=task.task_id,
        previous_status=task.status,
        new_status="Completed",
        changed_by=user_id,
        changed_at=datetime.utcnow(),
        note="User completed task",
    )
    db.add(history)

    # Update task status
    task.status = "Completed"
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


def approve_task(db: Session, task_id: int, manager_id: int):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    # Only managers or admins can approve - caller should check role
    history = TaskHistory(
        task_id=task.task_id,
        previous_status=task.status,
        new_status="Approved",
        changed_by=manager_id,
        changed_at=datetime.utcnow(),
        note="Manager approved task",
    )
    db.add(history)

    task.status = "Approved"
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
