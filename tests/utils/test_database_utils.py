from unittest.mock import MagicMock

from pytest_mock import MockFixture

from otter_welcome_buddy.common.utils import database


def test_get_cache_connection_string() -> None:
    # Arrange
    mock_database_string: str = "test.db"

    # Act
    result = database.get_cache_connection_string(mock_database_string)

    # Assert
    assert result == "sqlite:///" + mock_database_string


def test_get_cache_engine(
    mocker: MockFixture,
) -> None:
    # Arrange
    mock_engine = MagicMock()

    mock_connection_string = mocker.patch.object(
        database,
        "get_cache_connection_string",
        return_value="test.db",
    )
    mock_create_engine = mocker.patch.object(
        database,
        "create_engine",
        return_value=mock_engine,
    )

    # Act
    database.get_cache_engine("test.db")

    # Assert
    mock_connection_string.assert_called_once()
    mock_create_engine.assert_called_once()


def test_create_cache_session(
    mocker: MockFixture,
) -> None:
    # Arrange
    mock_engine = MagicMock()
    mock_session_maker = MagicMock()

    mock_get_cache_engine = mocker.patch.object(
        database,
        "get_cache_engine",
        return_value=mock_engine,
    )
    mock_sessionmaker = mocker.patch.object(
        database,
        "sessionmaker",
        return_value=mock_session_maker,
    )

    # Act
    database.create_cache_session("test.db")

    # Assert
    mock_get_cache_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()
