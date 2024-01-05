from mongoengine import CASCADE
from mongoengine import Document
from mongoengine import IntField
from mongoengine import ListField
from mongoengine import ReferenceField

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


class BaseRoleConfigModel(Document):
    """
    A model that represents the configuration to get the base role for the server in the database.

    Attributes:
        guild (GuildModel):     Reference to the guild that the activity belongs to
        message_ids (int):      List of message identifiers that the user needs to react to
    """

    guild = ReferenceField(GuildModel, reverse_delete_rule=CASCADE, primary_key=True)
    message_ids = ListField(IntField(required=True))
