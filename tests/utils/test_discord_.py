from unittest.mock import AsyncMock

import discord
import pytest
from discord.ext.commands import Bot
from discord.ext.commands import Context
from pytest_mock import MockFixture

from otter_welcome_buddy.common.utils import discord_


@pytest.mark.asyncio
async def test_send_plain_message(mock_ctx: Context) -> None:
    # Arrange
    test_msg: str = "Test message"

    mock_ctx.send = AsyncMock()

    # Act
    await discord_.send_plain_message(mock_ctx, test_msg)

    # Assert
    mock_ctx.send.assert_called_once_with(
        embed=discord.Embed(description=test_msg, color=discord.Color.teal()),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("is_in_cache", [True, False])
async def test_getGuildById_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_guild: discord.Guild,
    is_in_cache: bool,
) -> None:
    # Arrange
    mocked_guild_id: int = 111
    mock_guild.id = mocked_guild_id

    mock_get_guild = mocker.patch.object(
        mock_bot,
        "get_guild",
        return_value=mock_guild if is_in_cache else None,
    )
    mock_fetch_guild = mocker.patch.object(
        mock_bot,
        "fetch_guild",
        new=AsyncMock(return_value=mock_guild),
    )

    # Act
    result = await discord_.get_guild_by_id(mock_bot, mocked_guild_id)

    # Assert
    mock_get_guild.assert_called_once_with(mocked_guild_id)
    if is_in_cache:
        mock_fetch_guild.assert_not_called()
    else:
        mock_fetch_guild.assert_called_once_with(mocked_guild_id)
    assert result == mock_guild


@pytest.mark.asyncio
@pytest.mark.parametrize("is_in_cache", [True, False])
async def test_getChannelById_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_text_channel: discord.TextChannel,
    is_in_cache: bool,
) -> None:
    # Arrange
    mocked_channel_id: int = 111
    mock_text_channel.id = mocked_channel_id

    mock_get_channel = mocker.patch.object(
        mock_bot,
        "get_channel",
        return_value=mock_text_channel if is_in_cache else None,
    )
    mock_fetch_channel = mocker.patch.object(
        mock_bot,
        "fetch_channel",
        new=AsyncMock(return_value=mock_text_channel),
    )

    # Act
    result = await discord_.get_channel_by_id(mock_bot, mocked_channel_id)

    # Assert
    mock_get_channel.assert_called_once_with(mocked_channel_id)
    if is_in_cache:
        mock_fetch_channel.assert_not_called()
    else:
        mock_fetch_channel.assert_called_once_with(mocked_channel_id)
    assert result == mock_text_channel


@pytest.mark.asyncio
@pytest.mark.parametrize("channel_exists", [True, False])
async def test_getMessageById_Succeed(
    mocker: MockFixture,
    mock_bot: Bot,
    mock_text_channel: discord.TextChannel,
    mock_message: discord.Message,
    channel_exists: bool,
) -> None:
    # Arrange
    mocked_channel_id: int = 111
    mock_text_channel.id = mocked_channel_id
    mocked_message_id: int = 222
    mock_message.id = mocked_message_id

    mocker.patch.object(discord_, "isinstance", return_value=channel_exists)
    mock_get_channel_by_id = mocker.patch.object(
        discord_,
        "get_channel_by_id",
        new=AsyncMock(return_value=mock_text_channel if channel_exists else None),
    )
    mock_fetch_message = mocker.patch.object(
        mock_text_channel,
        "fetch_message",
        new=AsyncMock(return_value=mock_message),
    )

    # Act
    result = await discord_.get_message_by_id(mock_bot, mocked_channel_id, mocked_message_id)

    # Assert
    mock_get_channel_by_id.assert_called_once_with(mock_bot, mocked_channel_id)
    if channel_exists:
        mock_fetch_message.assert_called_once_with(mocked_message_id)
        assert result == (mock_message, mock_text_channel)
    else:
        mock_fetch_message.assert_not_called()
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("is_in_cache", [True, False])
async def test_getMemberById_Succeed(
    mocker: MockFixture,
    mock_guild: discord.Guild,
    mock_member: discord.Member,
    is_in_cache: bool,
) -> None:
    # Arrange
    mocked_member_id: int = 111
    mock_member.id = mocked_member_id

    mock_get_member = mocker.patch.object(
        mock_guild,
        "get_member",
        return_value=mock_member if is_in_cache else None,
    )
    mock_fetch_member = mocker.patch.object(
        mock_guild,
        "fetch_member",
        new=AsyncMock(return_value=mock_member),
    )

    # Act
    result = await discord_.get_member_by_id(mock_guild, mocked_member_id)

    # Assert
    mock_get_member.assert_called_once_with(mocked_member_id)
    if is_in_cache:
        mock_fetch_member.assert_not_called()
    else:
        mock_fetch_member.assert_called_once_with(mocked_member_id)
    assert result == mock_member
