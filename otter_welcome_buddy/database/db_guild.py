from sqlalchemy.orm import Session

from otter_welcome_buddy.database.models.guild_model import GuildModel


class DbGuild:
    """Class to interact with the table guild via static methods"""

    @staticmethod
    def get_guild(
        guild_id: int,
        session: Session,
    ) -> GuildModel | None:
        """Static method to get a guild by its id"""
        guild_model: GuildModel | None = (
            session.query(GuildModel).filter_by(id=guild_id).one_or_none()
        )
        return guild_model

    @staticmethod
    def insert_guild(
        guild_model: GuildModel,
        session: Session,
    ) -> GuildModel:
        """Static method to insert a guild record"""
        guild_model = session.merge(guild_model)
        return guild_model

    @staticmethod
    def delete_guild(
        guild_id: int,
        session: Session,
    ) -> None:
        """Static method to delete an interview match record by a guild_id"""
        session.query(GuildModel).filter_by(guild_id=guild_id).delete()
