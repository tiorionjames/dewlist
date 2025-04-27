from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth import get_current_user
from models import User
from routes import log_audit_action  # (✅ You already have this)


def RoleChecker(allowed_roles: list[str]):
    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if user.role not in allowed_roles:
            await log_audit_action(user, "Unauthorized access attempt", db)
            raise HTTPException(status_code=403, detail="Not authorized")
        return user

    return checker
