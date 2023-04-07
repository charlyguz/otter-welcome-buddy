from unittest.mock import MagicMock

from pytest_mock import MockFixture

from otter_welcome_buddy.common.utils.database import create_session
from otter_welcome_buddy.common.utils.database import get_engine
from otter_welcome_buddy.common.utils.database import get_sqlite_connection_string


def test_get_sqlite_connection_string() -> None:
    # Arrange
    mock_database_string: str = "test.db"

    # Act
    result = get_sqlite_connection_string(mock_database_string)

    # Assert
    assert result == "sqlite:///" + mock_database_string


def test_get_engine(
    mocker: MockFixture,
):
    # Arrange
    mock_engine = MagicMock()

    mock_connection_string = mocker.patch(
        "otter_welcome_buddy.common.utils.database.get_sqlite_connection_string",
        return_value="test.db",
    )
    mock_create_engine = mocker.patch(
        "otter_welcome_buddy.common.utils.database.create_engine",
        return_value=mock_engine,
    )

    # Act
    get_engine("test.db")

    # Assert
    mock_connection_string.assert_called_once()
    mock_create_engine.assert_called_once()


def test_create_session(
    mocker: MockFixture,
):
    # Arrange
    mock_engine = MagicMock()
    mock_session_maker = MagicMock()

    mock_get_engine = mocker.patch(
        "otter_welcome_buddy.common.utils.database.get_engine",
        return_value=mock_engine,
    )
    mock_sessionmaker = mocker.patch(
        "otter_welcome_buddy.common.utils.database.sessionmaker",
        return_value=mock_session_maker,
    )

    # Act
    create_session("test.db")

    # Assert
    mock_get_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()
