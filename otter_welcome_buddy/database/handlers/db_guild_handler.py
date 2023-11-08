from mongoengine import DoesNotExist

from otter_welcome_buddy.database.models.external.guild_model import GuildModel


class DbGuildHandler:
    """Class to interact with the table guild via static methods"""

    @staticmethod
    def get_guild(guild_id: int) -> GuildModel | None:
        """Static method to get a guild by its id"""
        try:
            guild_model: GuildModel = GuildModel.objects(guild_id=guild_id).get()
            return guild_model
        except DoesNotExist:
            return None

    @staticmethod
    def insert_guild(guild_model: GuildModel) -> GuildModel:
        """Static method to insert a guild record"""
        guild_model = guild_model.save()
        return guild_model

    @staticmethod
    def delete_guild(guild_id: int) -> None:
        """Static method to delete an interview match record by a guild_id"""
        guild_model: GuildModel | None = GuildModel.objects(guild_id=guild_id).first()
        if guild_model:
            guild_model.delete()
