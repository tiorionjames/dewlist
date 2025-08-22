# server/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import Task, User
from server.utils.task_helpers import get_task

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(User).filter(User.user_id == admin_id).first()
    if not admin or admin.role != "Admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    task = get_task(db, task_id)
    db.delete(task)
    db.commit()
    return {"detail": f"Task {task_id} deleted"}
