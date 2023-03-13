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

from otter_welcome_buddy.cogs import new_user_joins

if TYPE_CHECKING:
    from discord.types.gateway import MessageReactionAddEvent


@pytest.mark.asyncio
async def test_cogSetup_registerCommand(mock_bot):
    # Arrange
    mock_bot.add_cog = AsyncMock()

    # Act
    await new_user_joins.setup(mock_bot)

    # Assert
    assert mock_bot.add_cog.called


@pytest.mark.asyncio
async def test_onReady_printMessage(mock_bot, mock_msg_fmt, mock_debug_fmt):
    # Arrange
    cog = new_user_joins.Greetings(mock_bot, mock_msg_fmt, mock_debug_fmt)

    # Act
    await cog.on_ready()

    # Assert
    assert mock_debug_fmt.bot_is_ready.called


@pytest.mark.asyncio
@patch("otter_welcome_buddy.cogs.new_user_joins.WELCOME_MESSAGES", new=["111"])
async def test_onRawReactionAdd_addRole(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
    mock_role: Role,
    mock_msg_fmt,
    mock_debug_fmt,
):
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = new_user_joins.Greetings(mock_bot, mock_msg_fmt, mock_debug_fmt)
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


def test_commandMessage_correctMessage(mock_bot, mock_msg_fmt, mock_debug_fmt):
    # Act
    cog = new_user_joins.Greetings(mock_bot, mock_msg_fmt, mock_debug_fmt)
    cog._command_message()

    # Assert
    assert mock_msg_fmt.welcome_message.called
