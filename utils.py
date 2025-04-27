from datetime import datetime
from models import AuditLog
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


async def log_audit_action(
    user_id: int, action: str, detail: str = "", db: AsyncSession = Depends(get_db)
):
    log = AuditLog(user_id=user_id, action=action, detail=detail)
    db.add(log)
    await db.commit()


def strip_timezone(dt: datetime) -> datetime:
    if dt is not None and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def sanitize_datetime_fields(data: dict) -> dict:
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = strip_timezone(value)
    return data
