from mongoengine import CASCADE
from mongoengine import Document
from mongoengine import IntField
from mongoengine import ReferenceField

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


class AnnouncementsConfigModel(Document):
    """
    A model that indicates where to send the announcements.

    Attributes:
        guild (GuildModel):     Reference to the guild that want to receive the announcements
        channel_id (int):       Channel identifier where to send the announcement
    """

    guild = ReferenceField(GuildModel, reverse_delete_rule=CASCADE, primary_key=True)
    channel_id = IntField(required=True)
