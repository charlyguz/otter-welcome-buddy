from mongoengine import DoesNotExist

from otter_welcome_buddy.database.models.external.interview_match_model import InterviewMatchModel


class DbInterviewMatchHandler:
    """Class to interact with the table interview_match via static methods"""

    @staticmethod
    def get_interview_match(
        guild_id: int,
    ) -> InterviewMatchModel | None:
        """Static method to get an interview match by its guild_id"""
        try:
            interview_match_model: InterviewMatchModel = InterviewMatchModel.objects(
                guild=guild_id,
            ).get()
            return interview_match_model
        except DoesNotExist:
            return None

    @staticmethod
    def get_day_interview_matches(
        weekday: int,
    ) -> list[InterviewMatchModel]:
        """Static method to get all the interview matches for a day"""
        interview_match_models: list[InterviewMatchModel] = list(
            InterviewMatchModel.objects(day_of_the_week=weekday),
        )
        return interview_match_models

    @staticmethod
    def insert_interview_match(interview_match_model: InterviewMatchModel) -> InterviewMatchModel:
        """Static method to insert (or update) an interview match record"""
        interview_match_model = interview_match_model.save()
        return interview_match_model

    @staticmethod
    def delete_interview_match(guild_id: int) -> None:
        """Static method to delete an interview match record by a guild_id"""
        interview_match_model: InterviewMatchModel | None = InterviewMatchModel.objects(
            guild=guild_id,
        ).first()
        if interview_match_model:
            interview_match_model.delete()
