from mongoengine import DoesNotExist

from otter_welcome_buddy.database.models.external.role_config_model import BaseRoleConfigModel


class DbRoleConfigHandler:
    """Class to interact with the table role_config via static methods"""

    @staticmethod
    def get_base_role_config(
        guild_id: int,
    ) -> BaseRoleConfigModel | None:
        """Static method to get the base role config by its guild_id"""
        try:
            base_role_config_model: BaseRoleConfigModel = BaseRoleConfigModel.objects(
                guild=guild_id,
            ).get()
            return base_role_config_model
        except DoesNotExist:
            return None

    @staticmethod
    def get_all_base_role_configs() -> list[BaseRoleConfigModel]:
        """Static method to get all the base role configs in the database"""
        base_role_config_models: list[BaseRoleConfigModel] = list(BaseRoleConfigModel.objects())
        return base_role_config_models

    @staticmethod
    def insert_base_role_config(base_role_config_model: BaseRoleConfigModel) -> BaseRoleConfigModel:
        """Static method to insert (or update) a base role config record"""
        base_role_config_model = base_role_config_model.save()
        return base_role_config_model

    @staticmethod
    def delete_base_role_config(guild_id: int) -> None:
        """Static method to delete a base role config record by a guild_id"""
        base_role_config_model: BaseRoleConfigModel | None = BaseRoleConfigModel.objects(
            guild=guild_id,
        ).first()
        if base_role_config_model:
            base_role_config_model.delete()

    @staticmethod
    def delete_message_from_base_role_config(
        guild_id: int,
        input_message_id: int,
    ) -> BaseRoleConfigModel | None:
        """Static method to delete a base role config record by a guild_id"""
        base_role_config_model: BaseRoleConfigModel | None = BaseRoleConfigModel.objects(
            guild=guild_id,
        ).first()

        if not base_role_config_model:
            return None

        base_role_config_model.message_ids = [
            message_id
            for message_id in base_role_config_model.message_ids
            if message_id != input_message_id
        ]
        return DbRoleConfigHandler.insert_base_role_config(base_role_config_model)
