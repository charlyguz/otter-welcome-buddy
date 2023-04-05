from unittest.mock import AsyncMock

import pytest

from otter_welcome_buddy.cogs import new_user_joins


@pytest.mark.asyncio
async def test_cogSetup_registerCommand(mock_bot):
    # Arrange
    mock_bot.add_cog = AsyncMock()

    # Act
    await new_user_joins.setup(mock_bot)

    # Assert
    assert mock_bot.add_cog.called


def test_commandMessage_correctMessage(mock_bot, mock_msg_fmt):
    # Act
    cog = new_user_joins.Greetings(mock_bot, mock_msg_fmt)
    cog._command_message()

    # Assert
    assert mock_msg_fmt.welcome_message.called
