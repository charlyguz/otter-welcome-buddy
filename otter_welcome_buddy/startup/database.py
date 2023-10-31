from discord.ext.commands import Bot

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.utils.database import get_cache_engine
from otter_welcome_buddy.database.dbconn import BaseModel


async def init_database(_bot: Bot) -> None:
    """Initialize the database from the existing models"""

    # Initialize local database used as cache - Sqlite3
    engine = get_cache_engine(db_path=DATA_FILE_PATH)
    BaseModel.metadata.create_all(engine)
