import pytest
from mongoengine import DoesNotExist
from mongoengine import ValidationError
from mongomock import MongoClient

from otter_welcome_buddy.database.handlers.db_interview_match_handler import DbInterviewMatchHandler
from otter_welcome_buddy.database.models.external.guild_model import GuildModel
from otter_welcome_buddy.database.models.external.interview_match_model import InterviewMatchModel


def test_get_interview_match_succeed(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_interview_match_model: InterviewMatchModel = InterviewMatchModel(
        guild=mocked_guild_id,
        author_id=123,
        channel_id=123,
        day_of_the_week=0,
    )
    mocked_interview_match_model.save()

    # Act
    result = DbInterviewMatchHandler.get_interview_match(guild_id=mocked_guild_id)

    # Assert
    assert result is not None
    assert result.guild.id == mocked_guild_id


def test_get_interview_match_not_found(temporary_mongo_connection: MongoClient) -> None:
    # Act
    result = DbInterviewMatchHandler.get_interview_match(guild_id=123)

    # Assert
    assert result is None


def test_insert_interview_match_succeed(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_interview_match_model: InterviewMatchModel = InterviewMatchModel(
        guild=mocked_guild_id,
        author_id=123,
        channel_id=123,
        day_of_the_week=0,
    )

    # Act
    result = DbInterviewMatchHandler.insert_interview_match(
        interview_match_model=mocked_interview_match_model,
    )

    # Assert
    assert result is not None
    assert result.guild.guild_id == mocked_guild_id


def test_insert_interview_match_failed(temporary_mongo_connection: MongoClient) -> None:
    # Arrange
    mocked_interview_match_model: InterviewMatchModel = InterviewMatchModel()

    # Act / Assert
    with pytest.raises(ValidationError):
        DbInterviewMatchHandler.insert_interview_match(
            interview_match_model=mocked_interview_match_model,
        )


def test_delete_interview_match_valid_id(
    temporary_mongo_connection: MongoClient,
    mock_guild_model: GuildModel,
) -> None:
    # Arrange
    mocked_guild_id: int = mock_guild_model.guild_id
    mocked_interview_match_model: InterviewMatchModel = InterviewMatchModel(
        guild=mocked_guild_id,
        author_id=123,
        channel_id=123,
        day_of_the_week=0,
    )
    mocked_interview_match_model.save()

    # Act
    DbInterviewMatchHandler.delete_interview_match(guild_id=mocked_guild_id)

    # Assert
    with pytest.raises(DoesNotExist):
        InterviewMatchModel.objects(guild=mocked_guild_id).get()


def test_delete_interview_match_invalid_id(temporary_mongo_connection: MongoClient) -> None:
    # Act
    DbInterviewMatchHandler.delete_interview_match(guild_id=123)

    # Assert
    with pytest.raises(DoesNotExist):
        InterviewMatchModel.objects(guild=123).get()
