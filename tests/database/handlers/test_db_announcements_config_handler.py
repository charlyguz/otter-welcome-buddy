import pytest
from mongoengine import DoesNotExist
from mongoengine import ValidationError
from mongomock import MongoClient

from otter_welcome_buddy.database.handlers.db_announcements_config_handler import (
    DbAnnouncementsConfigHandler,
)
from otter_welcome_buddy.database.models.external.announcements_config_model import (
    AnnouncementsConfigModel,
)
from otter_welcome_buddy.database.models.external.guild_model import GuildModel


def test_get_announcements_config_succeed(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel(
        guild=mocked_guild_id,
        channel_id=123,
    )
    mocked_announcements_config_model.save()

    # Act
    result = DbAnnouncementsConfigHandler.get_announcements_config(guild_id=mocked_guild_id)

    # Assert
    assert result is not None
    assert result.guild.id == mocked_guild_id


def test_get_announcements_config_not_found(temporary_mongo_connection: MongoClient) -> None:
    # Act
    result = DbAnnouncementsConfigHandler.get_announcements_config(guild_id=123)

    # Assert
    assert result is None


def test_get_all_announcements_configs(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel(
        guild=mocked_guild_id,
        channel_id=123,
    )
    mocked_announcements_config_model.save()

    # Act
    results = DbAnnouncementsConfigHandler.get_all_announcements_configs()

    # Assert
    assert len(results) == 1
    assert results[0].guild.id == mocked_guild_id


def test_insert_announcements_config_succeed(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel(
        guild=mocked_guild_id,
        channel_id=123,
    )

    # Act
    result = DbAnnouncementsConfigHandler.insert_announcements_config(
        announcements_config_model=mocked_announcements_config_model,
    )

    # Assert
    assert result is not None
    assert result.guild.guild_id == mocked_guild_id


def test_insert_announcements_config_failed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel()

    # Act / Assert
    with pytest.raises(ValidationError):
        DbAnnouncementsConfigHandler.insert_announcements_config(
            announcements_config_model=mocked_announcements_config_model,
        )


def test_delete_announcements_config_valid_id(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel(
        guild=mocked_guild_id,
        channel_id=123,
    )
    mocked_announcements_config_model.save()

    # Act
    DbAnnouncementsConfigHandler.delete_announcements_config(guild_id=mocked_guild_id)

    # Assert
    with pytest.raises(DoesNotExist):
        AnnouncementsConfigModel.objects(guild=mocked_guild_id).get()


def test_delete_announcements_config_invalid_id(temporary_mongo_connection: MongoClient) -> None:
    # Act
    DbAnnouncementsConfigHandler.delete_announcements_config(guild_id=123)

    # Assert
    with pytest.raises(DoesNotExist):
        AnnouncementsConfigModel.objects(guild=123).get()
