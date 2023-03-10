import os
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest
from discord import Guild
from discord import Member
from discord import Role
from discord.ext.commands import Bot

from otter_welcome_buddy.database.models.guild_model import GuildModel
from otter_welcome_buddy.database.models.interview_match_model import InterviewMatchModel


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
def mock_database_session():
    mock_database_session = MagicMock()
    return mock_database_session


@pytest.fixture()
def temporary_database():
    db_path = "test.db"
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture()
def mock_guild_model() -> GuildModel:
    mock_guild_model = GuildModel(
        id=123,
    )
    return mock_guild_model


@pytest.fixture()
def mock_interview_match_model() -> InterviewMatchModel:
    guild = MagicMock()
    guild.id = 1
    mock_interview_match_model = InterviewMatchModel(
        guild_id=guild.id,
        guild=guild,
        author_id=2,
        channel_id=3,
        day_of_the_week=4,
        emoji="🤦‍♂",
        message_id=5,
    )
    return mock_interview_match_model
