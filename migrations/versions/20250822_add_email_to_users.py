# /migrations/versions/20250822_add_email_to_users.py
"""add email to users table

Revision ID: 20250822_add_email
Revises: 20250822_add_email_to_users.py
Create Date: 2025-08-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250822_add_email"
down_revision = "20250822_add_email_to_users.py"
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: add as nullable to avoid breaking existing rows
    op.add_column("users", sa.Column("email", sa.String(length=64), nullable=True))

    # Step 2: backfill existing users with placeholder emails
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE users
        SET email = CONCAT(username, '+', user_id::text, '@example.local')
        WHERE email IS NULL
        """
    )

    # Step 3: add unique constraint
    op.create_unique_constraint("uq_users_email", "users", ["email"])

    # Step 4: enforce NOT NULL
    op.alter_column("users", "email", nullable=False)


def downgrade():
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.drop_column("users", "email")
