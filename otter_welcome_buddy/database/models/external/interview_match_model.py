from mongoengine import CASCADE
from mongoengine import Document
from mongoengine import IntField
from mongoengine import ReferenceField
from mongoengine import StringField

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


class InterviewMatchModel(Document):
    """
    A model that represents an interview match activity in the database.

    Attributes:
        guild (GuildModel):     Reference to the guild that the activity belongs to
        author_id (int):        Extra user (usually the owner) used when odd number of participants
        channel_id (int):       Channel identifier where the activity takes place
        day_of_the_week (int):  Number identifying where the activity is run where 0 is Sunday
        emoji (str):            Emoji that should be used to react to take part of the activity
        message_id (int):       Identifier of the message that will be processed for the activity
    """

    guild = ReferenceField(GuildModel, reverse_delete_rule=CASCADE, primary_key=True)
    author_id = IntField(required=True)
    channel_id = IntField(required=True)
    day_of_the_week = IntField(required=True)
    emoji = StringField()
    message_id = IntField()

    meta = {"indexes": [{"fields": ["day_of_the_week"]}]}
