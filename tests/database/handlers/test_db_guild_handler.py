import pytest
from mongoengine import DoesNotExist
from mongoengine import ValidationError
from mongomock import MongoClient

from otter_welcome_buddy.database.handlers.db_guild_handler import DbGuildHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel


def test_get_guild_succeed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_guild_id: int = 123
    mocked_guild_model: GuildModel = GuildModel(
        guild_id=mocked_guild_id,
    )
    mocked_guild_model.save()

    # Act
    result = DbGuildHandler.get_guild(guild_id=mocked_guild_id)

    # Assert
    assert result is not None
    assert result.id == mocked_guild_id


def test_get_guild_not_found(temporary_mongo_connection: MongoClient) -> None:
    # Act
    result = DbGuildHandler.get_guild(guild_id=123)

    # Assert
    assert result is None


def test_insert_guild_succeed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_guild_id: int = 123
    mocked_guild_model: GuildModel = GuildModel(
        guild_id=mocked_guild_id,
    )

    # Act
    result = DbGuildHandler.insert_guild(guild_model=mocked_guild_model)

    # Assert
    assert result is not None
    assert result.id == mocked_guild_id


def test_insert_guild_failed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_guild_model: GuildModel = GuildModel()

    # Act / Assert
    with pytest.raises(ValidationError):
        DbGuildHandler.insert_guild(guild_model=mocked_guild_model)


def test_delete_guild_valid_id(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_guild_id: int = 123
    mocked_guild_model: GuildModel = GuildModel(
        guild_id=mocked_guild_id,
    )
    mocked_guild_model.save()

    # Act
    DbGuildHandler.delete_guild(guild_id=mocked_guild_id)

    # Assert
    with pytest.raises(DoesNotExist):
        GuildModel.objects(guild_id=mocked_guild_id).get()


def test_delete_guild_invalid_id(temporary_mongo_connection: MongoClient) -> None:
    # Act
    DbGuildHandler.delete_guild(guild_id=123)

    # Assert
    with pytest.raises(DoesNotExist):
        GuildModel.objects(guild_id=123).get()
