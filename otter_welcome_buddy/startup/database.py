from discord.ext.commands import Bot

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.utils.database import get_engine
from otter_welcome_buddy.database.db_guild import DbGuild
from otter_welcome_buddy.database.dbconn import BaseModel
from otter_welcome_buddy.database.dbconn import session_scope
from otter_welcome_buddy.database.models.guild_model import GuildModel


async def init_database(bot: Bot) -> None:
    """Initialize the database from the existing models"""
    engine = get_engine(db_path=DATA_FILE_PATH)
    BaseModel.metadata.create_all(engine)

    # Verify that all the guilds that the bot is part of are in the database
    for guild in bot.guilds:
        with session_scope() as session:
            if DbGuild.get_guild(guild_id=guild.id, session=session) is None:
                guild_model = GuildModel(id=guild.id)
                DbGuild.insert_guild(guild_model=guild_model, session=session)
