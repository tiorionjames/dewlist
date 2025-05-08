# /app/utils.py

from datetime import datetime
from passlib.context import CryptContext
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AuditLog

# ─────────────────────────────────────────────────────────────────────────────
# Password hashing utilities

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain-text password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────────────────────────────────────
# Audit-logging helper


async def log_audit_action(
    user_id: int,
    action: str,
    target: str = "",
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Record an audit log entry for the given user ID and action.
    """
    entry = AuditLog(user_id=user_id, action=action, target=target)
    db.add(entry)
    await db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Datetime sanitization helpers


def strip_timezone(dt: datetime) -> datetime:
    """Remove tzinfo from a datetime, if present."""
    if dt is not None and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def sanitize_datetime_fields(data: dict) -> dict:
    """
    Scan a dict for datetime values and strip their tzinfo.
    """
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = strip_timezone(value)
    return data
