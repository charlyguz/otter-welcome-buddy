from mongoengine import DoesNotExist

from otter_welcome_buddy.database.models.external.announcements_config_model import (
    AnnouncementsConfigModel,
)


class DbAnnouncementsConfigHandler:
    """Class to interact with the table announcements_config via static methods"""

    @staticmethod
    def get_announcements_config(
        guild_id: int,
    ) -> AnnouncementsConfigModel | None:
        """Static method to get an announcement config by its guild_id"""
        try:
            announcements_config_model: AnnouncementsConfigModel = AnnouncementsConfigModel.objects(
                guild=guild_id,
            ).get()
            return announcements_config_model
        except DoesNotExist:
            return None

    @staticmethod
    def get_all_announcements_configs() -> list[AnnouncementsConfigModel]:
        """Static method to get all the interview matches for a day"""
        announcements_config_models: list[AnnouncementsConfigModel] = list(
            AnnouncementsConfigModel.objects(),
        )
        return announcements_config_models

    @staticmethod
    def insert_announcements_config(
        announcements_config_model: AnnouncementsConfigModel,
    ) -> AnnouncementsConfigModel:
        """Static method to insert (or update) an announcement config record"""
        announcements_config_model = announcements_config_model.save()
        return announcements_config_model

    @staticmethod
    def delete_announcements_config(guild_id: int) -> None:
        """Static method to delete an announcement config record by a guild_id"""
        announcements_config_model: AnnouncementsConfigModel | None = (
            AnnouncementsConfigModel.objects(
                guild=guild_id,
            ).first()
        )
        if announcements_config_model:
            announcements_config_model.delete()
