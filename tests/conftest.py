import os
from collections.abc import Callable
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from discord import Guild
from discord import Member
from discord import Role
from discord.ext.commands import Bot
from discord.ext.commands import Context
from mongoengine import connect as mongo_connect
from mongoengine import disconnect as mongo_disconnect
from mongomock import MongoClient

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


@pytest.fixture
def mock_ctx() -> Context:
    mocked_ctx = AsyncMock()
    return mocked_ctx


@pytest.fixture
def mock_bot() -> Bot:
    mocked_bot = AsyncMock()
    return mocked_bot


@pytest.fixture
def mock_guild() -> Guild:
    mocked_guild = Mock()
    return mocked_guild


@pytest.fixture
def make_mock_member() -> Callable[[int, str], Member]:
    def _make_mock_member(id: int = 123, name: str = "Test Member") -> Member:
        mocked_member = Mock()
        mocked_member.id = id
        mocked_member.name = name
        mocked_member.display_name = name

        return mocked_member

    return _make_mock_member


@pytest.fixture
def mock_member(make_mock_member: Callable[[int, str], Member]) -> Member:
    return make_mock_member()


@pytest.fixture
def mock_role() -> Role:
    mocked_role = Mock()
    return mocked_role


@pytest.fixture
def mock_msg_fmt():
    mocked_msg_fmt = MagicMock()
    mocked_msg_fmt.bot_is_ready = MagicMock()
    return mocked_msg_fmt


@pytest.fixture
def mock_debug_fmt():
    mocked_debug_fmt = MagicMock()
    mocked_debug_fmt.welcome_message = MagicMock()
    return mocked_debug_fmt


@pytest.fixture()
def mock_cache_session():
    mocked_cache_session = MagicMock()
    return mocked_cache_session


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
    mocked_guild_model = GuildModel(
        guild_id=123,
    )
    mocked_guild_model.save()
    return mocked_guild_model
