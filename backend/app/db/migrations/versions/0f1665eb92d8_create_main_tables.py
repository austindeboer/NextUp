"""create_main_tables
Revision ID: 0f1665eb92d8
Revises:
Create Date: 2021-02-28 22:05:11.545689
"""
from alembic import op
import sqlalchemy as sa
from typing import Tuple


# revision identifiers, used by Alembic
revision = "12345678654"
down_revision = None
branch_labels = None
depends_on = None

def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )
def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )

def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),        
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="False"),     
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_profiles_table() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.Text, nullable=True),
        sa.Column("phone_number", sa.Text, nullable=True),
        sa.Column("bio", sa.Text, nullable=True, server_default=""),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_profiles_modtime
            BEFORE UPDATE
            ON profiles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def create_todos_table() -> None:
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("task", sa.Text, nullable=False, index=True),
        sa.Column("completed", sa.Boolean, nullable=False),
        sa.Column("owner", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),  
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_todos_modtime
            BEFORE UPDATE
            ON todos
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_profiles_table()
    create_todos_table()

def downgrade() -> None: 
    op.drop_table("todos")
    op.drop_table("profiles")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
