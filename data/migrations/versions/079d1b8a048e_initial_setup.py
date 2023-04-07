"""initial setup

Revision ID: 079d1b8a048e
Revises:
Create Date: 2023-04-06 21:28:09.061276

"""
import sqlalchemy as sa
from alembic import op

from otter_welcome_buddy.database.models.guild_model import GuildModel


# revision identifiers, used by Alembic.
revision = "079d1b8a048e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, GuildModel.__tablename__):
        op.create_table(
            "guild",
            sa.Column("id", sa.BigInteger(), nullable=False, primary_key=True),
        )


def downgrade() -> None:
    op.drop_table("guild")
