from typing import Any

from otter_welcome_buddy.common.utils.types.interview_match import InterviewMatchType
from otter_welcome_buddy.database.db_helpers import delete
from otter_welcome_buddy.database.db_helpers import dict_factory
from otter_welcome_buddy.database.db_helpers import fetch_all
from otter_welcome_buddy.database.db_helpers import fetch_one
from otter_welcome_buddy.database.db_helpers import insert_one
from otter_welcome_buddy.database.db_helpers import update


class DbInterviewMatch:
    """Class to interact with the table interview_match via static methods"""

    TABLE: str = "interview_match"

    @staticmethod
    def get_interview_match(guild_id: int) -> Any:
        """Static method to get an interview match by its guild_id"""
        return fetch_one(
            table=DbInterviewMatch.TABLE,
            lookup_key={"guild_id": guild_id},
            row_factory=dict_factory,
        )

    @staticmethod
    def get_interview_matches() -> list:
        """Static method to get all the interview matches"""
        return fetch_all(
            table=DbInterviewMatch.TABLE,
            row_factory=dict_factory,
        )

    @staticmethod
    def get_day_interview_matches(weekday: int) -> list:
        """Static method to get all the interview matches for a day"""
        return fetch_all(
            table=DbInterviewMatch.TABLE,
            lookup_key={"day_of_the_week": weekday},
            row_factory=dict_factory,
        )

    @staticmethod
    def insert_interview_match(interview_match: InterviewMatchType) -> int:
        """Static method to insert (or replace) an interview match record"""
        return insert_one(
            table=DbInterviewMatch.TABLE,
            columns=list(interview_match.keys()),
            values=tuple(interview_match.values()),
        )

    @staticmethod
    def update_interview_match(interview_match: InterviewMatchType) -> int:
        """Static method to update an interview match record"""
        return update(
            table=DbInterviewMatch.TABLE,
            columns=["message_id"],
            values=(interview_match["message_id"],),
            lookup_key={"guild_id": interview_match["guild_id"]},
        )

    @staticmethod
    def delete_interview_match(guild_id: int) -> int:
        """Static method to delete an interview match record by a guild_id"""
        return delete(
            table=DbInterviewMatch.TABLE,
            lookup_key={"guild_id": guild_id},
        )
