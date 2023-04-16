from sqlalchemy.orm import Session

from otter_welcome_buddy.database.models.leetcode_model import LeetcodeUserModel


class DbLeetcodeUser:
    """Class to interact with the table leetcode_user via static methods"""

    @staticmethod
    def get_leetcode_user(
        handle: str,
        session: Session,
    ) -> LeetcodeUserModel | None:
        """Static method to get a leetcode_user by its handle"""
        leetcode_user_model: LeetcodeUserModel | None = session.query(LeetcodeUserModel).filter_by(handle=handle).one_or_none()
        return leetcode_user_model

    @staticmethod
    def insert_leetcode_user(
        leetcode_user_model: LeetcodeUserModel,
        session: Session,
        override: bool = False,
    ) -> LeetcodeUserModel:
        """Static method to insert a leetcode_user record"""
        if not override:
            current_leetcode_user_model = DbLeetcodeUser.get_leetcode_user(handle=leetcode_user_model.handle, session=session)
            if current_leetcode_user_model is None:
                session.add(leetcode_user_model)
                return leetcode_user_model
            return current_leetcode_user_model
        leetcode_user_model = session.merge(leetcode_user_model)
        return leetcode_user_model

    @staticmethod
    def delete_leetcode_user(
        handle: str,
        session: Session,
    ) -> None:
        """Static method to delete an leetcode_user record by its handle"""
        session.query(LeetcodeUserModel).filter_by(handle=handle).delete()
