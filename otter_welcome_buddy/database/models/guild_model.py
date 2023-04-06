from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from otter_welcome_buddy.database.dbconn import BaseModel


class GuildModel(BaseModel):
    """A model that represents a guild (server) in the database.

    Attributes:
        id (int):   The identifier for the guild, is taken from discord records and is the primary
                    key of the object
    """

    __tablename__ = "guild"

    id = Column(BigInteger, primary_key=True)
    interview_match = relationship("InterviewMatchModel", uselist=False, cascade="all, delete-orphan")
