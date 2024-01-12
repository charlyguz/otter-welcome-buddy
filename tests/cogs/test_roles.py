from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from discord import Guild
from discord import Member
from discord import PartialEmoji
from discord import RawReactionActionEvent
from discord import Role
from discord.ext.commands import Bot
from pytest_mock import MockFixture

from otter_welcome_buddy.cogs import roles

if TYPE_CHECKING:
    from discord.types.gateway import MessageReactionAddEvent


@pytest.fixture(autouse=True)
def mock_init_welcome_messages(mocker: MockFixture) -> None:
    mocker.patch.object(roles.Roles, "_init_welcome_messages")


@pytest.mark.asyncio
async def test_onRawReactionAdd_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
) -> None:
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = roles.Roles(mock_bot)
    data: MessageReactionAddEvent = {
        "user_id": 111,
        "channel_id": 111,
        "message_id": 111,
        "guild_id": mock_guild.id,
    }
    payload = RawReactionActionEvent(
        data=data,
        emoji=PartialEmoji(name="😀"),
        event_type="REACTION_ADD",
    )
    mock_member.id = 111
    payload.member = mock_member

    mock_welcome_messages = mocker.patch.object(roles.Roles, "_check_welcome_message_reaction")
    mock_roles_reaction = mocker.patch.object(roles.Roles, "_check_roles_reaction")

    # Act
    await cog.on_raw_reaction_add(payload)

    # Assert
    mock_welcome_messages.assert_called_once()
    mock_roles_reaction.assert_called_once()


@pytest.mark.asyncio
async def test_onRawReactionRemove_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
) -> None:
    # Arrange
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    cog = roles.Roles(mock_bot)
    data: MessageReactionAddEvent = {
        "user_id": 111,
        "channel_id": 111,
        "message_id": 111,
        "guild_id": mock_guild.id,
    }
    payload = RawReactionActionEvent(
        data=data,
        emoji=PartialEmoji(name="😀"),
        event_type="REACTION_REMOVE",
    )
    mock_member.id = 111
    payload.member = mock_member

    mock_welcome_messages = mocker.patch.object(roles.Roles, "_check_welcome_message_reaction")
    mock_roles_reaction = mocker.patch.object(roles.Roles, "_check_roles_reaction")

    # Act
    await cog.on_raw_reaction_remove(payload)

    # Assert
    mock_welcome_messages.assert_not_called()
    mock_roles_reaction.assert_called_once()


@pytest.mark.asyncio
async def test__checkWelcomeMessageReaction_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
    mock_role: Role,
) -> None:
    # Arrange
    mocked_message_id = 111
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    mock_member.id = 111
    mock_guild.members = [mock_member]
    mock_guild.roles = [mock_role]

    cog = roles.Roles(mock_bot)
    cog._WELCOME_MESSAGES_CONFIG = {mock_guild.id: [mocked_message_id]}

    mock_get_guild = mocker.patch.object(
        roles,
        "get_guild_by_id",
        new=AsyncMock(return_value=mock_guild),
    )
    mock_get_member = mocker.patch.object(
        roles,
        "get_member_by_id",
        new=AsyncMock(return_value=mock_member),
    )
    mock_get_role = mocker.patch("discord.utils.get", return_value=mock_role)
    mock_add_roles = mocker.patch.object(Member, "add_roles")

    # Act
    await cog._check_welcome_message_reaction(
        mock_guild.id,
        mock_member,
        mock_member.id,
        mocked_message_id,
    )

    # Assert
    mock_get_guild.assert_called_once()
    mock_get_member.assert_not_called()
    mock_get_role.assert_called_once()
    mock_add_roles.assert_called_once()


@pytest.mark.parametrize("is_add_reaction", [True, False])
@pytest.mark.asyncio
async def test__checkRolesReaction_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: Guild,
    mock_member: Member,
    mock_role: Role,
    is_add_reaction: bool,
) -> None:
    # Arrange
    mocked_message_id = 111
    mock_guild.id = 111
    mock_bot.guilds = [mock_guild]
    mock_member.id = 111
    mock_guild.members = [mock_member]
    mock_guild.roles = [mock_role]
    mock_emoji = "😀"

    cog = roles.Roles(mock_bot)
    cog._REACTION_ROLES_CONFIG = {mocked_message_id: {mock_emoji: mock_role.id}}

    mock_get_guild = mocker.patch.object(
        roles,
        "get_guild_by_id",
        new=AsyncMock(return_value=mock_guild),
    )
    mock_get_member = mocker.patch.object(
        roles,
        "get_member_by_id",
        new=AsyncMock(return_value=mock_member),
    )
    mock_get_role = mocker.patch("discord.utils.get", return_value=mock_role)
    mock_add_roles = mocker.patch.object(Member, "add_roles")
    mock_remove_roles = mocker.patch.object(Member, "remove_roles")

    # Act
    await cog._check_roles_reaction(
        mock_guild.id,
        mock_member,
        mock_member.id,
        mocked_message_id,
        PartialEmoji(name=mock_emoji),
        is_add_reaction,
    )

    # Assert
    mock_get_guild.assert_called_once()
    mock_get_member.assert_not_called()
    mock_get_role.assert_called_once()
    if is_add_reaction:
        mock_add_roles.assert_called_once()
        mock_remove_roles.assert_not_called()
    else:
        mock_add_roles.assert_not_called()
        mock_remove_roles.assert_called_once()
