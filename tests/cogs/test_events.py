from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from discord import Guild
from discord import Member
from discord import PartialEmoji
from discord import RawReactionActionEvent
from discord import Role
from discord.ext.commands import Bot
from pytest_mock import MockFixture

from otter_welcome_buddy.cogs import events
from otter_welcome_buddy.database.db_guild import DbGuild
from otter_welcome_buddy.database.models.guild_model import GuildModel

if TYPE_CHECKING:
    from discord.types.gateway import MessageReactionAddEvent


@pytest.mark.asyncio
async def test_cogSetup_registerCommand(mock_bot):
    # Arrange
    mock_bot.add_cog = AsyncMock()

    # Act
    await events.setup(mock_bot)

    # Assert
    assert mock_bot.add_cog.called


@pytest.mark.asyncio
async def test_onReady_printMessage(mock_bot, mock_debug_fmt):
    # Arrange
    cog = events.BotEvents(mock_bot, mock_debug_fmt)

    # Act
    await cog.on_ready()

    # Assert
    assert mock_debug_fmt.bot_is_ready.called


@pytest.mark.asyncio
@patch("otter_welcome_buddy.cogs.events.WELCOME_MESSAGES", new=["111"])
async def test_onRawReactionAdd_addRole(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
    mock_role: Role,
    mock_debug_fmt,
):
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = events.BotEvents(mock_bot, mock_debug_fmt)
    data: MessageReactionAddEvent = {
        "user_id": 111,
        "channel_id": 111,
        "message_id": 111,
        "guild_id": 111,
    }
    payload = RawReactionActionEvent(
        data=data,
        emoji=PartialEmoji(name="😀"),
        event_type="REACTION_ADD",
    )
    payload.member = mock_member

    mock_get_role = mocker.patch("discord.utils.get", return_value=mock_role)
    mock_add_roles = mocker.patch.object(Member, "add_roles")

    # Act
    await cog.on_raw_reaction_add(payload)

    # Assert
    mock_get_role.assert_called_once()
    mock_add_roles.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_new_guild", [True, False])
async def test_onGuildJoin_insertDb(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_debug_fmt,
    mock_database_session,
    mock_guild_model: GuildModel,
    is_new_guild: bool,
):
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = events.BotEvents(mock_bot, mock_debug_fmt)

    mock_session = mocker.patch(
        "otter_welcome_buddy.database.dbconn.create_session",
        return_value=mock_database_session,
    )
    mock_get_guild = mocker.patch.object(
        DbGuild,
        "get_guild",
        return_value=None if is_new_guild else mock_guild_model,
    )
    mock_insert_guild = mocker.patch.object(DbGuild, "insert_guild")

    # Act
    await cog.on_guild_join(mock_guild)

    # Assert
    mock_session.assert_called_once()
    mock_get_guild.assert_called_once_with(
        guild_id=mock_guild.id,
        session=mock_database_session,
    )
    if is_new_guild:
        mock_insert_guild.assert_called_once()
    else:
        mock_insert_guild.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_existing_guild", [True, False])
async def test_onGuildRemove_deleteDb(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_debug_fmt,
    mock_database_session,
    mock_guild_model: GuildModel,
    is_existing_guild: bool,
):
    # Arrange
    mock_guild.id = mock_guild_model.id
    mock_bot.guilds = [mock_guild]
    cog = events.BotEvents(mock_bot, mock_debug_fmt)

    mock_session = mocker.patch(
        "otter_welcome_buddy.database.dbconn.create_session",
        return_value=mock_database_session,
    )
    mock_get_guild = mocker.patch.object(
        DbGuild,
        "get_guild",
        return_value=mock_guild_model if is_existing_guild else None,
    )
    mock_delete_guild = mocker.patch.object(DbGuild, "delete_guild")

    # Act
    await cog.on_guild_remove(mock_guild)

    # Assert
    mock_session.assert_called_once()
    mock_get_guild.assert_called_once_with(
        guild_id=mock_guild_model.id,
        session=mock_database_session,
    )
    if is_existing_guild:
        mock_delete_guild.assert_called_once()
    else:
        mock_delete_guild.assert_not_called()
