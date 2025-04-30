# /app/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from schemas import UserCreate, ForgotPasswordRequest
from utils import get_password_hash, verify_password
from uuid import uuid4
from datetime import datetime, timedelta


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_password_reset_token(
    db: AsyncSession, user_id: int, expires_delta: timedelta = timedelta(hours=1)
) -> str:
    token = str(uuid4())
    expire_at = datetime.utcnow() + expires_delta
    # assume you have a PasswordReset model/table
    from models import PasswordReset

    reset = PasswordReset(user_id=user_id, token=token, expires_at=expire_at)
    db.add(reset)
    await db.commit()
    await db.refresh(reset)
    return token


async def send_reset_email(email: str, token: str) -> None:
    reset_link = f"https://yourdomain.com/reset-password?token={token}"
    # replace with real mailer (FastAPI-Mail, SendGrid, etc.)
    print(f"[DEBUG] send email to {email}: {reset_link}")
