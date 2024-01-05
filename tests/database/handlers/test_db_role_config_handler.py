import pytest
from mongoengine import DoesNotExist
from mongoengine import ValidationError
from mongomock import MongoClient

from otter_welcome_buddy.database.handlers.db_role_config_handler import DbRoleConfigHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel
from otter_welcome_buddy.database.models.external.role_config_model import BaseRoleConfigModel


@pytest.fixture
def mock_base_role_config_model(mock_guild_model: GuildModel) -> BaseRoleConfigModel:
    mocked_base_role_config_model = BaseRoleConfigModel(
        guild=mock_guild_model,
        message_ids=[123],
    )
    return mocked_base_role_config_model


def test_get_base_role_config_succeed(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_base_role_config_model.guild.id
    mock_base_role_config_model.save()

    # Act
    result = DbRoleConfigHandler.get_base_role_config(guild_id=mocked_guild_id)

    # Assert
    assert result is not None
    assert result.guild.id == mocked_guild_id
    assert len(result.message_ids) == 1


def test_get_base_role_config_not_found(temporary_mongo_connection: MongoClient) -> None:
    # Act
    result = DbRoleConfigHandler.get_base_role_config(guild_id=123)

    # Assert
    assert result is None


def test_get_all_base_role_configs_succeed(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mock_base_role_config_model.save()

    # Act
    results = DbRoleConfigHandler.get_all_base_role_configs()

    # Assert
    assert len(results) == 1


def test_get_all_base_role_configs_empty(
    temporary_mongo_connection: MongoClient,
) -> None:
    # Act
    results = DbRoleConfigHandler.get_all_base_role_configs()

    # Assert
    assert len(results) == 0


def test_insert_base_role_config_succeed(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_base_role_config_model.guild.id

    # Act
    result = DbRoleConfigHandler.insert_base_role_config(
        base_role_config_model=mock_base_role_config_model,
    )

    # Assert
    assert result is not None
    assert result.guild.guild_id == mocked_guild_id


def test_insert_base_role_config_failed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_base_role_config_model: BaseRoleConfigModel = BaseRoleConfigModel()

    # Act / Assert
    with pytest.raises(ValidationError):
        DbRoleConfigHandler.insert_base_role_config(
            base_role_config_model=mocked_base_role_config_model,
        )


def test_delete_base_role_config_valid_id(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_base_role_config_model.guild.id
    mock_base_role_config_model.save()

    # Act
    DbRoleConfigHandler.delete_base_role_config(guild_id=mocked_guild_id)

    # Assert
    with pytest.raises(DoesNotExist):
        BaseRoleConfigModel.objects(guild=mocked_guild_id).get()


def test_delete_base_role_config_invalid_id(temporary_mongo_connection: MongoClient) -> None:
    # Act
    DbRoleConfigHandler.delete_base_role_config(guild_id=123)

    # Assert
    with pytest.raises(DoesNotExist):
        BaseRoleConfigModel.objects(guild=123).get()


def test_delete_message_from_base_role_config_valid_id(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_base_role_config_model.guild.id
    mock_base_role_config_model.message_ids = [123, 456, 789]
    mock_base_role_config_model.save()

    # Act
    result = DbRoleConfigHandler.delete_message_from_base_role_config(
        guild_id=mocked_guild_id,
        input_message_id=123,
    )

    # Assert
    assert result is not None
    assert result.guild.id == mocked_guild_id
    assert len(result.message_ids) == 2


def test_delete_message_from_base_role_config_invalid_id(
    temporary_mongo_connection: MongoClient,
    mock_base_role_config_model: BaseRoleConfigModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_base_role_config_model.guild.id
    mock_base_role_config_model.message_ids = [123, 456, 789]
    mock_base_role_config_model.save()

    # Act
    result = DbRoleConfigHandler.delete_message_from_base_role_config(
        guild_id=mocked_guild_id,
        input_message_id=0,
    )

    # Assert
    assert result is not None
    assert result.guild.id == mocked_guild_id
    assert len(result.message_ids) == 3
