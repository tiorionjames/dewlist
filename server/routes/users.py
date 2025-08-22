from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from alembic import op
from server.database import get_db
from server.models import User
from server.schemas import UserOut
import sqlalchemy as sa

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# revision identifiers, used by Alembic
revision = "123456789abc"
down_revision = "<previous_revision_id>"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email", sa.String(), nullable=False, unique=True))


def downgrade():
    op.drop_column("users", "email")
