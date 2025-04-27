database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://<user>:<pass>@localhost/<dbname>"


engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


docker-compose.yml
version: '2.4'

services:
  dewlist:
    build: .
    container_name: dewlist-app
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/dewlist
      - SECRET_KEY=your_super_secret_key_here
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30

    entrypoint: ["/wait-for-it.sh", "db", "5432", "--"]
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

  db:
    image: postgres:15
    container_name: dewlist-db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: dewlist
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:


Dockerfile
FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from sqlalchemy.exc import OperationalError

import models
from database import engine
from routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_database():
    for i in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.create_all)
            print("Database is ready!")
            return
        except OperationalError:
            print(f"Database not ready, retry {i+1}/10…")
            await asyncio.sleep(1)
    raise RuntimeError("Could not connect to the database after 10 attempts")


@app.on_event("startup")
async def on_startup():
    await initialize_database()


app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Welcome to DewList!"}



models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tasks = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_complete = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    recurrence = Column(String, nullable=True)
    recurrence_end = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    pause_reason = Column(String, nullable=True)
    resumed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="tasks")


requirements.txt
accelerate==1.6.0
aiofiles==24.1.0
aiohappyeyeballs==2.6.1
aiohttp==3.11.16
aiosignal==1.3.2
annotated-types==0.7.0
anyio==4.9.0
async-timeout==5.0.1
asyncpg==0.30.0
attrs==25.3.0
base==0.0.0
bcrypt==4.3.0
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==3.4.1
click==8.1.8
contourpy==1.3.1
cryptography==44.0.2
cycler==0.12.1
datasets==3.5.0
dill==0.3.8
dnspython==2.7.0
ecdsa==0.19.1
email_validator==2.2.0
exceptiongroup==1.2.2
fastapi==0.115.12
fastapi-cli==0.0.7
ffmpy==0.5.0
filelock==3.18.0
fonttools==4.57.0
frozenlist==1.5.0
fsspec==2024.12.0
gradio==5.25.0
gradio_client==1.8.0
greenlet==3.2.0
groovy==0.1.2
h11==0.14.0
httpcore==1.0.8
httptools==0.6.4
httpx==0.28.1
huggingface-hub==0.30.2
idna==3.10
Jinja2==3.1.6
kiwisolver==1.4.8
llvmlite==0.44.0
Markdown==3.8
markdown-it-py==3.0.0
MarkupSafe==3.0.2
matplotlib==3.10.1
mdurl==0.1.2
mpmath==1.3.0
multidict==6.4.3
multiprocess==0.70.16
networkx==3.4.2
numba==0.61.2
numpy==2.2.4
orjson==3.10.16
packaging==24.2
pandas==2.2.3
passlib==1.7.4
pillow==11.2.1
propcache==0.3.1
psutil==7.0.0
psycopg==3.2.6
psycopg2-binary==2.9.10
pyarrow==19.0.1
pyasn1==0.4.8
pycparser==2.22
pydantic==2.11.3
pydantic_core==2.33.1
pydub==0.25.1
Pygments==2.19.1
pyparsing==3.2.3
python-dateutil==2.9.0.post0
python-dotenv==1.1.0
python-jose==3.4.0
python-multipart==0.0.20
pytz==2025.2
PyYAML==6.0.2
regex==2024.11.6
requests==2.32.3
rich==14.0.0
rich-toolkit==0.14.1
rsa==4.9.1
ruff==0.11.5
safehttpx==0.1.6
safetensors==0.5.3
semantic-version==2.10.0
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.40
starlette==0.46.2
sympy==1.13.3
tokenizers==0.21.1
tomlkit==0.13.2
torch==2.2.2
torchaudio==2.2.2
torchvision==0.17.2
tqdm==4.67.1
transformers==4.51.2
typer==0.15.2
typing-inspection==0.4.0
typing_extensions==4.13.2
tzdata==2025.2
urllib3==2.4.0
uvicorn==0.34.1
uvloop==0.21.0
watchfiles==1.0.5
websockets==15.0.1
xxhash==3.5.0
yarl==1.19.0



routes.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import Optional

import models, schemas
from database import get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    create_reset_token,
    verify_reset_token,
)

router = APIRouter()


@router.post("/register", response_model=schemas.UserOut)
async def register(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.User).where(models.User.email == form_data.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/tasks", response_model=schemas.TaskOut)
async def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_task = models.Task(**task.dict(), user_id=current_user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.get("/tasks", response_model=list[schemas.TaskOut])
async def get_tasks(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    due: Optional[str] = Query(None, regex="^(overdue|today|upcoming)$"),
):
    query = select(models.Task).where(models.Task.user_id == current_user.id)
    now = datetime.utcnow()
    if due == "overdue":
        query = query.where(
            models.Task.due_date < now, models.Task.is_complete == False
        )
    elif due == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        query = query.where(models.Task.due_date >= start, models.Task.due_date < end)
    elif due == "upcoming":
        query = query.where(models.Task.due_date > now)
    result = await db.execute(query)
    tasks = result.scalars().all()

    def build_label(task):
        if task.recurrence and task.recurrence_end:
            return f"Repeats {task.recurrence} until {task.recurrence_end.date()}"
        elif task.recurrence:
            return f"Repeats {task.recurrence}"
        return None

    return [
        schemas.TaskOut(**task.__dict__, recurrence_label=build_label(task))
        for task in tasks
    ]


@router.put("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(
    task_id: int,
    updated_task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/complete", response_model=schemas.TaskOut)
async def toggle_complete(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.is_complete:
        task.is_complete = False
        task.completed_at = None
    else:
        task.is_complete = True
        task.completed_at = datetime.utcnow()
        if task.recurrence and task.due_date:
            delta_map = {
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1),
                "monthly": timedelta(days=30),
                "yearly": timedelta(days=365),
            }
            next_delta = delta_map.get(task.recurrence)
            if next_delta:
                next_due = task.due_date + next_delta
                if not task.recurrence_end or next_due <= task.recurrence_end:
                    new_task = models.Task(
                        title=task.title,
                        description=task.description,
                        due_date=next_due,
                        recurrence=task.recurrence,
                        recurrence_end=task.recurrence_end,
                        user_id=current_user.id,
                    )
                    db.add(new_task)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.patch("/tasks/{task_id}/start", response_model=schemas.TaskOut)
async def start_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Task).where(models.Task))



schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    recurrence_end: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    user_id: int
    is_complete: bool
    completed_at: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    paused_at: Optional[datetime]
    pause_reason: Optional[str]
    resumed_at: Optional[datetime]
    recurrence_label: Optional[str]

    class Config:
        from_attributes = True


class Message(BaseModel):
    detail: str
