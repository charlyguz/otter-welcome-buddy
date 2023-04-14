from typing import Any
from typing import NamedTuple
from typing import TypedDict

from typing_extensions import NotRequired


class GraphqlDataRequestType(TypedDict):
    """Data format to send the request to GraphQL"""

    query: str
    variables: NotRequired[dict[str, Any]]


class PublicProfileType(NamedTuple):
    """Response type received from GraphQL with the profile information"""

    countryName: str | None
    ranking: int
    userAvatar: str


class UserPublicProfileType(NamedTuple):
    """Response type received from GraphQL for the user public profile"""

    username: str
    profile: PublicProfileType

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserPublicProfileType":
        """Return a UserPublicProfileType built from a dict"""
        profile_info = PublicProfileType(**data["profile"])
        return cls(data["username"], profile_info)


class UserRecentAcSubmissionType(NamedTuple):
    """Response type received from GraphQL for the recent submissions of a user"""

    id: str
    titleSlug: str
    timestamp: str


class ProblemSolvedType(NamedTuple):
    """Response type received from GraphQL with the problem information"""

    titleSlug: str
    questionId: str
    difficulty: str


class UserProblemSolvedType(NamedTuple):
    """Response type received from GraphQL with the information about a user problem"""

    nProblems: int
    question: ProblemSolvedType
