from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from otter_welcome_buddy.database.dbconn import BaseModel


_INTERVIEW_MATCH_MODEL_TABLE_NAME = "interview_match"


class InterviewMatchModel(BaseModel):
    """A model that represents an interview match activity in the database.

    Attributes:
        guild_id (int): Foreign key referring to the guild that is associated to this activity
        author_id (int): Wildcard user (usually the owner) used when odd number of participants
        channel_id (int): Channel identifier where the activity takes place
        day_of_the_week (int): Number identifying where the activity is run where 0 is Sunday
        emoji (str): Emoji that should be used to react to take part of the activity
        message_id (int): Identifier of the message that will be processed for the activity
    """

    __tablename__ = _INTERVIEW_MATCH_MODEL_TABLE_NAME

    guild_id = Column(BigInteger, ForeignKey("guild.id"), primary_key=True)
    guild = relationship("GuildModel")
    author_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    day_of_the_week = Column(Integer)
    emoji = Column(String)
    message_id = Column(BigInteger, nullable=True)
