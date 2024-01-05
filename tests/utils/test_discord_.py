import discord
import pytest
from discord.ext.commands import Context
from pytest_mock import MockFixture

from otter_welcome_buddy.common.utils import discord_


@pytest.mark.asyncio
async def test_send_plain_message(mocker: MockFixture, mock_ctx: Context) -> None:
    # Arrange
    test_msg: str = "Test message"

    mock_ctx_send = mocker.patch.object(mock_ctx, "send")

    # Act
    await discord_.send_plain_message(mock_ctx, test_msg)

    # Assert
    mock_ctx_send.assert_called_once_with(
        embed=discord.Embed(description=test_msg, color=discord.Color.teal()),
    )
