from sqlalchemy.orm import Session

from otter_welcome_buddy.database.models.interview_match_model import InterviewMatchModel


class DbInterviewMatch:
    """Class to interact with the table interview_match via static methods"""

    @staticmethod
    def get_interview_match(
        guild_id: int,
        session: Session,
    ) -> InterviewMatchModel | None:
        """Static method to get an interview match by its guild_id"""
        interview_match_model: InterviewMatchModel | None = session.query(InterviewMatchModel).get(
            guild_id,
        )
        return interview_match_model

    @staticmethod
    def get_day_interview_matches(
        weekday: int,
        session: Session,
    ) -> list[InterviewMatchModel]:
        """Static method to get all the interview matches for a day"""
        interview_match_models: list[InterviewMatchModel] = (
            session.query(InterviewMatchModel).filter_by(day_of_the_week=weekday).all()
        )
        return interview_match_models

    @staticmethod
    def upsert_interview_match(
        interview_match_model: InterviewMatchModel,
        session: Session,
    ) -> InterviewMatchModel:
        """Static method to insert (or update) an interview match record"""
        interview_match_model = session.merge(interview_match_model)
        return interview_match_model

    @staticmethod
    def delete_interview_match(
        guild_id: int,
        session: Session,
    ) -> None:
        """Static method to delete an interview match record by a guild_id"""
        session.query(InterviewMatchModel).filter_by(guild_id=guild_id).delete()
