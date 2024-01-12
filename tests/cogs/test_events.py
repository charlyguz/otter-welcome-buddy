from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from discord import Guild
from discord.ext.commands import Bot
from pytest_mock import MockFixture

from otter_welcome_buddy.cogs import events
from otter_welcome_buddy.database.handlers.db_guild_handler import DbGuildHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel


@pytest.mark.asyncio
async def test_cogSetup_registerCommand(mock_bot: Bot) -> None:
    # Arrange
    mock_bot.add_cog = AsyncMock()

    # Act
    await events.setup(mock_bot)

    # Assert
    assert mock_bot.add_cog.called


@pytest.mark.asyncio
async def test_onReady_printMessage(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_debug_fmt: MagicMock,
) -> None:
    # Arrange
    cog = events.BotEvents(mock_bot, mock_debug_fmt)
    mock_init_guild = mocker.patch("otter_welcome_buddy.cogs.events.init_guild_table")

    # Act
    await cog.on_ready()

    # Assert
    mock_init_guild.assert_called_once()
    assert mock_debug_fmt.bot_is_ready.called


@pytest.mark.asyncio
@pytest.mark.parametrize("is_new_guild", [True, False])
async def test_onGuildJoin_insertDb(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_debug_fmt: MagicMock,
    mock_guild_model: GuildModel,
    is_new_guild: bool,
) -> None:
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = events.BotEvents(mock_bot, mock_debug_fmt)

    mock_get_guild = mocker.patch.object(
        DbGuildHandler,
        "get_guild",
        return_value=None if is_new_guild else mock_guild_model,
    )
    mock_insert_guild = mocker.patch.object(DbGuildHandler, "insert_guild")

    # Act
    await cog.on_guild_join(mock_guild)

    # Assert
    mock_get_guild.assert_called_once_with(guild_id=mock_guild.id)
    if is_new_guild:
        mock_insert_guild.assert_called_once()
    else:
        mock_insert_guild.assert_not_called()


@pytest.mark.asyncio
async def test_onGuildRemove_deleteDb(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_debug_fmt: MagicMock,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mock_guild.id = mock_guild_model.id
    mock_bot.guilds = [mock_guild]
    cog = events.BotEvents(mock_bot, mock_debug_fmt)

    mock_delete_guild = mocker.patch.object(DbGuildHandler, "delete_guild")

    # Act
    await cog.on_guild_remove(mock_guild)

    # Assert
    mock_delete_guild.assert_called_once_with(guild_id=mock_guild.id)
