from typing import Any

import requests
from jsonschema import ValidationError

from otter_welcome_buddy.common.handlers.graphql import GraphQLClient
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_problem_solved_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_public_profile_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import (
    user_recent_ac_submissions_schema,
)
from otter_welcome_buddy.common.utils.types.handlers import ProblemSolvedType
from otter_welcome_buddy.common.utils.types.handlers import UserProblemSolvedType
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

_USER_RECENT_AC_SUBMISSIONS: str = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    titleSlug
    timestamp
  }
}
"""

_USER_PROBLEM_SOLVED: str = """
query userProblemSolved($username: String!, $titleSlug: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
  question(titleSlug: $titleSlug) {
    titleSlug
    questionId
    difficulty
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
            _USER_RECENT_AC_SUBMISSIONS,
            user_recent_ac_submissions_schema,
            variables,
        )
        if response is None:
            print("No user found")
            return None

        return [UserRecentAcSubmissionType(**item) for item in response["recentAcSubmissionList"]]

    def get_user_problem_solved(
        self,
        username: str,
        title_slug: str,
    ) -> UserProblemSolvedType | None:
        """
        Get the user count of problems along with the id, title slug and difficulty of a problem.
        """
        variables: dict[str, Any] = {
            "username": username,
            "titleSlug": title_slug,
        }
        response = self._fetch_request(_USER_PROBLEM_SOLVED, user_problem_solved_schema, variables)
        if response is None:
            print("No user found")
            return None

        n_problems = list(
            filter(
                lambda problem: problem["difficulty"] == "All",
                response["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"],
            ),
        )
        if len(n_problems) != 1:
            print("Error while getting the count of all problems")
            return None
        n_problems_all: dict[str, Any] = n_problems[0]

        question = ProblemSolvedType(**response["question"])
        return UserProblemSolvedType(int(n_problems_all["count"]), question)
