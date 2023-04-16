from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from otter_welcome_buddy.database.dbconn import BaseModel


class UserModel(BaseModel):
    """A model that represents an user in the database.

    Attributes:
        discord_id (int): Identifier of an user in Discord
        leetcode_handle (string): Username of the user in leetcode
    """

    __tablename__ = "user"

    discord_id = Column(BigInteger, primary_key=True)
    leetcode_handle = Column(String, ForeignKey('leetcode_user.handle'))
    leetcode_user = relationship('LeetcodeUserModel')
