from typing import TypedDict


class InterviewMatchType(TypedDict):
    """Interview Match object saved on the database"""

    guild_id: int
    author_id: int
    channel_id: int
    day_of_the_week: int
    emoji: int
    message_id: int | None
