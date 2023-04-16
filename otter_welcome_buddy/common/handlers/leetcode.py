from typing import Any

import requests
from jsonschema import ValidationError

from otter_welcome_buddy.common.handlers.graphql import GraphQLClient
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import problem_info_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import problemset_list_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_problems_solved_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_public_profile_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import (
    user_recent_ac_submissions_schema,
)
from otter_welcome_buddy.common.utils.types.handlers import ProblemInfoType
from otter_welcome_buddy.common.utils.types.handlers import ProblemsetListType
from otter_welcome_buddy.common.utils.types.handlers import UserProblemsSolvedType
from otter_welcome_buddy.common.utils.types.handlers import UserPublicProfileType
from otter_welcome_buddy.common.utils.types.handlers import UserRecentAcSubmissionType


_USER_PROFILE_QUERY: str = """
query userPublicProfile($username: String!) {
    matchedUser(username: $username) {
        username
        profile {
            countryName
            ranking
            userAvatar
        }
    }
}
"""

_USER_RECENT_AC_SUBMISSIONS_QUERY: str = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    titleSlug
    timestamp
  }
}
"""

_USER_PROBLEMS_SOLVED_QUERY: str = """
query userProblemSolved($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

_PROBLEM_INFO_QUERY: str = """
query userProblemSolved($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    titleSlug
    title
    questionId
    questionFrontendId
    difficulty
  }
}
"""

_PROBLEMSET_LIST_QUERY: str = """
query problemsetQuestionList(
    $categorySlug: String,
    $limit: Int,
    $filters: QuestionListFilterInput
) {
    problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        filters: $filters
    ) {
        total: totalNum
        questions: data {
            title
            titleSlug
            questionId
            questionFrontendId
            difficulty
        }
    }
}
"""


class LeetcodeAPI:
    """
    A class for making requests to the LeetCode API.
    """

    _RETRY_COUNT: int = 5

    _LEETCODE_URL: str = "https://leetcode.com/graphql/"

    def __init__(self) -> None:
        """
        Initialize the LeetCodeAPI object with the default graphql client to make the requests.
        """
        self.graphql_client = GraphQLClient(self._LEETCODE_URL)

    def _fetch_request(
        self,
        query: str,
        schema: dict[str, Any],
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Sends a request using the graphql client, if any exception is caught, fail silently returning None
        """
        try:
            response = self.graphql_client.make_request(query, schema, variables, self._RETRY_COUNT)
            return response
        except requests.exceptions.RequestException as ex:
            print(f"Error while fetching the request: {ex}")
            return None
        except ValidationError as ex:
            print(f"Invalid response received: {ex.message}")
            return None

    def get_user_public_profile(self, username: str) -> UserPublicProfileType | None:
        """
        Get the user public profile information for a given username, currently just getting the country name.
        """
        variables: dict[str, Any] = {
            "username": username,
        }

        response = self._fetch_request(_USER_PROFILE_QUERY, user_public_profile_schema, variables)
        if response is None:
            print("No user found")
            return None

        return UserPublicProfileType.from_dict(response["matchedUser"])

    def get_user_recent_ac_submissions(
        self,
        username: str,
        limit: int = 3,
    ) -> list[UserRecentAcSubmissionType] | None:
        """
        Get the user recent submissions, for each of them we get the id, the title slug and the timestamp.
        """
        variables: dict[str, Any] = {
            "username": username,
            "limit": limit,
        }

        response = self._fetch_request(
            _USER_RECENT_AC_SUBMISSIONS_QUERY,
            user_recent_ac_submissions_schema,
            variables,
        )
        if response is None:
            print("No user found")
            return None

        return [UserRecentAcSubmissionType(**item) for item in response["recentAcSubmissionList"]]

    def get_user_problems_solved(
        self,
        username: str,
    ) -> UserProblemsSolvedType | None:
        """
        Get the user count of problems along.
        """
        variables: dict[str, Any] = {
            "username": username,
        }
        response = self._fetch_request(_USER_PROBLEMS_SOLVED_QUERY, user_problems_solved_schema, variables)
        if response is None:
            print("No user found")
            return None

        solved_problems = dict(
            map(
                lambda problemsSolved: (f"{problemsSolved['difficulty'].lower()}Problems", problemsSolved["count"]),
                response["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"],
            ),
        )

        return UserProblemsSolvedType(**solved_problems)

    def get_problem_info(
        self,
        title_slug: str,
    ) -> ProblemInfoType | None:
        """
        Get the information of a problem based on its title_slug.
        """
        variables: dict[str, Any] = {
            "titleSlug": title_slug,
        }
        response = self._fetch_request(_PROBLEM_INFO_QUERY, problem_info_schema, variables)
        if response is None:
            print("No problem found")
            return None

        return ProblemInfoType(**response["question"])

    def get_problemset_list(
        self,
        limit: int = 5000,
        category_slug: str = "",
    ) -> ProblemsetListType | None:
        """
        Get the problemset list, can by in general or by its category
        """
        variables: dict[str, Any] = {
            "limit": limit,
            "categorySlug": category_slug,
            # Is required for the query, but I don't know what's it
            "filters": {},
        }
        response = self._fetch_request(_PROBLEMSET_LIST_QUERY, problemset_list_schema, variables)
        if response is None:
            print("No problems found")
            return None

        return ProblemsetListType.from_dict(response["problemsetQuestionList"])
