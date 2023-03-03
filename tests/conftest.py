from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_bot():
    mock_bot = AsyncMock()
    return mock_bot


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
