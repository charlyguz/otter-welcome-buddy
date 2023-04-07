"""add interview match table

Revision ID: 0924b3e7935e
Revises: 079d1b8a048e
Create Date: 2023-04-06 21:58:11.711405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0924b3e7935e"
down_revision = "079d1b8a048e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_match",
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=True),
        sa.Column("channel_id", sa.BigInteger(), nullable=True),
        sa.Column("day_of_the_week", sa.Integer(), nullable=True),
        sa.Column("emoji", sa.String(), nullable=True),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["guild_id"], ["guild.id"], ),
        sa.PrimaryKeyConstraint("guild_id"),
    )


def downgrade() -> None:
    op.drop_table("interview_match")
