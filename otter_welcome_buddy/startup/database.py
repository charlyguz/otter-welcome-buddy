from alembic import command
from alembic.config import Config
from discord.ext.commands import Bot
from sqlalchemy import Engine

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.utils.db_helpers import get_engine
from otter_welcome_buddy.database.db_guild import DbGuild
from otter_welcome_buddy.database.dbconn import BaseModel
from otter_welcome_buddy.database.dbconn import session_scope
from otter_welcome_buddy.database.models.guild_model import GuildModel


_ALEMBIC_CONFIG_FILE = "alembic.ini"


def init_guild_table(bot: Bot) -> None:
    """Verify that all the guilds that the bot is part of are in the database"""
    for guild in bot.guilds:
        print(f"Initializing guild {guild.name} [{guild.id}]")
        with session_scope() as session:
            guild_model = GuildModel(id=guild.id)
            DbGuild.insert_guild(guild_model=guild_model, session=session)


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
