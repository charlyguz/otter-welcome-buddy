import os
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from discord import Guild
from discord import Member
from discord import Role
from discord.ext.commands import Bot
from mongoengine import connect as mongo_connect
from mongoengine import disconnect as mongo_disconnect
from mongomock import MongoClient

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


@pytest.fixture
def mock_bot() -> Bot:
    mock_bot = AsyncMock()
    return mock_bot


@pytest.fixture
def mock_guild() -> Guild:
    mock_guild = Mock()
    return mock_guild


@pytest.fixture
def mock_member() -> Member:
    mock_member = Mock()
    return mock_member


@pytest.fixture
def mock_role() -> Role:
    mock_role = Mock()
    return mock_role


@pytest.fixture
def mock_msg_fmt():
    mock_msg_fmt = MagicMock()
    mock_msg_fmt.bot_is_ready = MagicMock()
    return mock_msg_fmt


@pytest.fixture
def mock_debug_fmt():
    mock_debug_fmt = MagicMock()
    mock_debug_fmt.welcome_message = MagicMock()
    return mock_debug_fmt


@pytest.fixture()
def mock_cache_session():
    mock_cache_session = MagicMock()
    return mock_cache_session


@pytest.fixture()
def temporary_cache():
    db_path = "test.db"
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture()
def temporary_mongo_connection():
    mock_mongo_connection = mongo_connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=MongoClient,
    )
    yield mock_mongo_connection
    mongo_disconnect()


@pytest.fixture()
def mock_guild_model(temporary_mongo_connection) -> GuildModel:
    mock_guild_model = GuildModel(
        guild_id=123,
    )
    mock_guild_model.save()
    return mock_guild_model
