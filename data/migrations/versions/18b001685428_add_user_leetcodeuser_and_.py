"""Add User, LeetcodeUser and LeetcodeProblem models

Revision ID: 18b001685428
Revises: 0924b3e7935e
Create Date: 2023-04-15 19:30:50.724101

"""
import sqlalchemy as sa
from alembic import op

from otter_welcome_buddy.database.models.guild_model import LeetcodeProblemModel
from otter_welcome_buddy.database.models.guild_model import LeetcodeUserModel
from otter_welcome_buddy.database.models.guild_model import UserModel


# revision identifiers, used by Alembic.
revision = "18b001685428"
down_revision = "0924b3e7935e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not op.get_bind().has_table(UserModel.__tablename__):
        op.create_table("user",
            sa.Column("discord_id", sa.BigInteger(), nullable=False),
            sa.Column("leetcode_handle", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("discord_id"),
            sa.ForeignKeyConstraint(["leetcode_handle"], ["leetcode_user.handle"], ),
            sa.UniqueConstraint("leetcode_handle")
        )

    if not op.get_bind().has_table(LeetcodeUserModel.__tablename__):
        op.create_table("leetcode_user",
            sa.Column("handle", sa.String(), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=True),
            sa.Column("user_avatar", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("handle"),
        )

    if not op.get_bind().has_table(LeetcodeProblemModel.__tablename__):
        op.create_table("leetcode_problem",
            sa.Column("question_slug", sa.String(), nullable=False),
            sa.Column("title", sa.String(), nullable=True),
            sa.Column("question_id", sa.Integer(), nullable=True),
            sa.Column("frontend_id", sa.Integer(), nullable=True),
            sa.Column("difficulty", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("question_slug"),
        )


def downgrade() -> None:
    op.drop_table("leetcode_problem")
    op.drop_table("leetcode_user")
    op.drop_table("user")
