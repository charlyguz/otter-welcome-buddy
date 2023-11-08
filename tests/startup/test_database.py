from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from discord import Guild
from discord.ext.commands import Bot
from pymongo import monitoring
from pytest_mock import MockFixture

from otter_welcome_buddy.database.handlers.db_guild_handler import DbGuildHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel
from otter_welcome_buddy.startup import database


@pytest.mark.parametrize("is_new_guild", [True, False])
def test_initGuildTable(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_guild_model: GuildModel,
    is_new_guild: bool,
) -> None:
    # Arrange
    mocked_guild_id = 123
    mocked_guild_name = "Test Guild"
    mock_guild.id = mocked_guild_id
    mock_guild.name = mocked_guild_name
    mock_bot.guilds = [mock_guild]

    mock_get_guild = mocker.patch.object(
        DbGuildHandler,
        "get_guild",
        return_value=None if is_new_guild else mock_guild_model,
    )
    mock_insert_guild = mocker.patch.object(DbGuildHandler, "insert_guild")

    # Act
    database.init_guild_table(bot=mock_bot)

    # Assert
    mock_get_guild.assert_called_once_with(guild_id=mocked_guild_id)
    if is_new_guild:
        mock_insert_guild.assert_called_once()
    else:
        mock_insert_guild.assert_not_called()


@pytest.mark.asyncio
@patch("otter_welcome_buddy.startup.database.BaseModel.metadata.create_all")
async def test_initDatabase(mock_create_all: MagicMock, mocker: MockFixture) -> None:
    # Arrange
    mock_engine = MagicMock()

    mock_get_cache_engine = mocker.patch.object(
        database,
        "get_cache_engine",
        return_value=mock_engine,
    )
    mock_monitoring_register = mocker.patch.object(monitoring, "register")
    mock_mongo_engine = mocker.patch.object(database, "mongo_connect")

    # Act
    await database.init_database()

    # Assert
    print(type(mock_create_all))
    mock_get_cache_engine.assert_called_once()
    mock_create_all.assert_called_once_with(mock_engine)
    mock_monitoring_register.assert_called_once()
    mock_mongo_engine.assert_called_once()
