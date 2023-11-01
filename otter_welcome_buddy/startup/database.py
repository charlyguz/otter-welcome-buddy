import os

from dotenv import load_dotenv
from mongoengine import connect as mongo_connect
from pymongo import monitoring

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.utils.database import get_cache_engine
from otter_welcome_buddy.database.dbconn import BaseModel
from otter_welcome_buddy.log.dblogger import DbCommandLogger


async def init_database() -> None:
    """Initialize the database from the existing models"""
    load_dotenv()

    # Initialize local database used as cache - Sqlite3
    engine = get_cache_engine(db_path=DATA_FILE_PATH)
    BaseModel.metadata.create_all(engine)

    # Connect to global database - MongoDB
    monitoring.register(DbCommandLogger())
    mongo_connect(host=os.environ["MONGO_URI"])
