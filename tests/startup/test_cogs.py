from unittest.mock import AsyncMock

import pytest

from otter_welcome_buddy.startup import cogs


def test_formatModulePath_cogExtensionFormat() -> None:
    # Arrange
    cog_path = cogs.hiring_timelines.__file__

    # Act
    format_path = cogs.__format_module_path_into_cog_extension(cog_path)

    # Assert
    assert format_path == "otter_welcome_buddy.cogs.hiring_timelines"


@pytest.mark.asyncio
async def test_loadExtensions_registerCogs() -> None:
    # Arrange
    mock_bot = AsyncMock()
    mock_bot.load_extension = AsyncMock()

    # Act
    await cogs.register_cogs(mock_bot)

    # Assert
    assert mock_bot.load_extension.call_count == 5
