"""create interview_match table

Revision ID: a9fa41ae7138
Revises:
Create Date: 2023-04-06 17:05:39.972718

"""
import sqlalchemy as sa
from alembic import op

from otter_welcome_buddy.database.models.interview_match_model import (
    _INTERVIEW_MATCH_MODEL_TABLE_NAME,
)


# revision identifiers, used by Alembic.
revision = "a9fa41ae7138"
down_revision = None
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
        sa.ForeignKeyConstraint(["guild_id"], ["guild.id"]),
        sa.PrimaryKeyConstraint("guild_id"),
    )
    op.add_column(
        "guild",
        sa.Column("interview_match_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(None, "guild", "interview_match", ["interview_match_id"], ["guild_id"])


def downgrade() -> None:
    op.drop_constraint(None, "guild", type_="foreignkey")
    op.drop_column("guild", "interview_match_id")
    op.drop_table("interview_match")
