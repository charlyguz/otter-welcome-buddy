from sqlalchemy.orm import Session

from otter_welcome_buddy.database.models.user_model import UserModel


class DbUser:
    """Class to interact with the table user via static methods"""

    @staticmethod
    def get_user(
        user_id: int,
        session: Session,
    ) -> UserModel | None:
        """Static method to get a user by its discord id"""
        user_model: UserModel | None = session.query(UserModel).filter_by(discord_id=user_id).one_or_none()
        return user_model

    @staticmethod
    def get_user_by_handle(
        handle: str,
        session: Session,
    ) -> UserModel | None:
        """Static method to get a user by its discord id"""
        user_model: UserModel | None = session.query(UserModel).filter_by(leetcode_handle=handle).one_or_none()
        return user_model

    @staticmethod
    def insert_user(
        user_model: UserModel,
        session: Session,
        override: bool = False,
    ) -> UserModel:
        """Static method to insert a user record"""
        if not override:
            current_user_model = DbUser.get_user(user_id=user_model.discord_id, session=session)
            if current_user_model is None:
                session.add(user_model)
                return user_model
            return current_user_model
        user_model = session.merge(user_model)
        return user_model

    @staticmethod
    def delete_user(
        user_id: int,
        session: Session,
    ) -> None:
        """Static method to delete an user record by its discord id"""
        session.query(UserModel).filter_by(discord_id=user_id).delete()
