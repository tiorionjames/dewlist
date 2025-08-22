# crud.py
from sqlalchemy.orm import Session
from extra import Task, TaskHistory
from datetime import datetime


def complete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return None
    # Only allow users to complete tasks assigned to them
    if task.assigned_to != user_id:
        raise Exception("Unauthorized")

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
    db.commit()
    db.refresh(task)
    return task


def approve_task(db: Session, task_id: int, manager_id: int):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return None
    # Only managers or admins can approve
    # (Check role in user table here)

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
    db.commit()
    db.refresh(task)
    return task
