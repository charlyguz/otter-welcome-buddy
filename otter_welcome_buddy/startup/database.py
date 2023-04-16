from alembic import command
from alembic.config import Config
from discord.ext.commands import Bot
from sqlalchemy import Engine

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.handlers.leetcode import LeetcodeAPI
from otter_welcome_buddy.common.utils.db_helpers import get_engine
from otter_welcome_buddy.common.utils.types.handlers import ProblemsetListType
from otter_welcome_buddy.database.db_guild import DbGuild
from otter_welcome_buddy.database.db_leetcode_problem import DbLeetcodeProblem
from otter_welcome_buddy.database.dbconn import BaseModel
from otter_welcome_buddy.database.dbconn import session_scope
from otter_welcome_buddy.database.models.guild_model import GuildModel
from otter_welcome_buddy.database.models.leetcode_model import LeetcodeProblemModel


_ALEMBIC_CONFIG_FILE = "alembic.ini"


def init_guild_table(bot: Bot) -> None:
    """Verify that all the guilds that the bot is part of are in the database"""
    for guild in bot.guilds:
        print(f"Initializing guild {guild.name} [{guild.id}]")
        with session_scope() as session:
            guild_model = GuildModel(id=guild.id)
            DbGuild.insert_guild(guild_model=guild_model, session=session)


def _update_leetcode_problems() -> None:
    """Update the leetcode problems in the database to be used as cache"""
    leetcode_client: LeetcodeAPI = LeetcodeAPI()
    problemset_list: ProblemsetListType | None = leetcode_client.get_problemset_list()
    if problemset_list is None:
        print("No problems fetched from Leetcode")
        return
    with session_scope() as session:
        for problem in problemset_list.questions:
            leetcode_problem_model: LeetcodeProblemModel = LeetcodeProblemModel(
                question_slug=problem.titleSlug,
                title=problem.title,
                question_id=int(problem.questionId),
                frontend_id=int(problem.questionFrontendId),
                difficulty=problem.difficulty,
            )
            DbLeetcodeProblem.insert_leetcode_problem(
                session=session,
                leetcode_problem_model=leetcode_problem_model,
            )


def _upgrade_database(engine: Engine) -> None:
    """Upgrade the database to the latest version using Alembic"""
    alembic_config = Config(_ALEMBIC_CONFIG_FILE)
    with engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")


def init_database() -> None:
    """Initialize the database from the existing models"""
    engine = get_engine(db_path=DATA_FILE_PATH)
    BaseModel.metadata.create_all(engine)

    _upgrade_database(engine=engine)
    _update_leetcode_problems()
