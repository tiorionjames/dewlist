# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    text,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    user = relationship("User", back_populates="audit_logs")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("0"))
    role = Column(String(50), nullable=False, server_default=text("'user'"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    tasks = relationship("Task", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_complete = Column(Boolean, nullable=False, server_default=text("0"))
    status = Column(
        String(30),
        nullable=False,
        server_default=text("'active'"),
        comment="active | pending_approval | approved",
    )
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    recurrence = Column(String(255), nullable=True)
    recurrence_end = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    pause_reason = Column(String(255), nullable=True)
    resumed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="tasks")


class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    user = relationship("User", back_populates="password_resets")
