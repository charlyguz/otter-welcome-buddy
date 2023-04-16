from sqlalchemy.orm import Session

from otter_welcome_buddy.database.models.leetcode_model import LeetcodeProblemModel


class DbLeetcodeProblem:
    """Class to interact with the table leetcode_problem via static methods"""

    @staticmethod
    def get_leetcode_problem(
        question_slug: str,
        session: Session,
    ) -> LeetcodeProblemModel | None:
        """Static method to get a leetcode_problem by its question_slug"""
        leetcode_problem_model: LeetcodeProblemModel | None = session.query(LeetcodeProblemModel).filter_by(question_slug=question_slug).one_or_none()
        return leetcode_problem_model

    @staticmethod
    def insert_leetcode_problem(
        leetcode_problem_model: LeetcodeProblemModel,
        session: Session,
        override: bool = False,
    ) -> LeetcodeProblemModel:
        """Static method to insert a leetcode_problem record"""
        if not override:
            current_leetcode_problem_model = DbLeetcodeProblem.get_leetcode_problem(question_slug=leetcode_problem_model.question_slug, session=session)
            if current_leetcode_problem_model is None:
                session.add(leetcode_problem_model)
                return leetcode_problem_model
            return current_leetcode_problem_model
        leetcode_problem_model = session.merge(leetcode_problem_model)
        return leetcode_problem_model

    @staticmethod
    def delete_leetcode_problem(
        question_slug: str,
        session: Session,
    ) -> None:
        """Static method to delete an leetcode_problem record by its question_slug"""
        session.query(LeetcodeProblemModel).filter_by(question_slug=question_slug).delete()
