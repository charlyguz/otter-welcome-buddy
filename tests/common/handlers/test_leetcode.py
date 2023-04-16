from typing import Any

import pytest
from jsonschema import ValidationError
from pytest_mock import MockFixture
from requests import RequestException

from otter_welcome_buddy.common.handlers.graphql import GraphQLClient
from otter_welcome_buddy.common.handlers.leetcode import _PROBLEM_INFO_QUERY
from otter_welcome_buddy.common.handlers.leetcode import _PROBLEMSET_LIST_QUERY
from otter_welcome_buddy.common.handlers.leetcode import _USER_PROBLEMS_SOLVED_QUERY
from otter_welcome_buddy.common.handlers.leetcode import _USER_PROFILE_QUERY
from otter_welcome_buddy.common.handlers.leetcode import _USER_RECENT_AC_SUBMISSIONS_QUERY
from otter_welcome_buddy.common.handlers.leetcode import LeetcodeAPI
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import problem_info_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import problemset_list_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_problems_solved_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_public_profile_schema
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import (
    user_recent_ac_submissions_schema,
)


@pytest.fixture
def mock_leetcodeapi() -> LeetcodeAPI:
    _mock_leetcodeapi = LeetcodeAPI()
    return _mock_leetcodeapi


def test__fetch_request_succeed(mocker: MockFixture, mock_leetcodeapi: LeetcodeAPI) -> None:
    # Arrange
    mock_query: str = "query { my_field }"
    mock_schema: dict[str, Any] = {"type": "object", "properties": {"my_field": {"type": "string"}}}
    mock_response_data: dict[str, Any] = {"my_field": "my_value"}

    mocked_make_request = mocker.patch.object(GraphQLClient, "make_request", return_value=mock_response_data)

    # Act
    result = mock_leetcodeapi._fetch_request(mock_query, mock_schema)

    # Assert
    assert result == mock_response_data
    mocked_make_request.assert_called_once()


def test__fetch_request_requestException(mocker: MockFixture, mock_leetcodeapi: LeetcodeAPI) -> None:
    # Arrange
    mock_query: str = "query { my_field }"
    mock_schema: dict[str, Any] = {"type": "object", "properties": {"my_field": {"type": "string"}}}
    mock_exception: RequestException = RequestException("Error fetching")

    mocked_make_request = mocker.patch.object(GraphQLClient, "make_request", side_effect=mock_exception)

    # Act
    result = mock_leetcodeapi._fetch_request(mock_query, mock_schema)

    # Assert
    assert result is None
    mocked_make_request.assert_called_once()


def test__fetch_request_validationError(mocker: MockFixture, mock_leetcodeapi: LeetcodeAPI) -> None:
    # Arrange
    mock_query: str = "query { my_field }"
    mock_schema: dict[str, Any] = {"type": "object", "properties": {"my_field": {"type": "string"}}}
    mock_exception: ValidationError = ValidationError("Error validating")

    mocked_make_request = mocker.patch.object(GraphQLClient, "make_request", side_effect=mock_exception)

    # Act
    result = mock_leetcodeapi._fetch_request(mock_query, mock_schema)

    # Assert
    assert result is None
    mocked_make_request.assert_called_once()


@pytest.mark.parametrize("is_valid_username", [True, False])
def test_get_user_public_profile(mocker: MockFixture, mock_leetcodeapi: LeetcodeAPI, is_valid_username: bool) -> None:
    # Arrange
    mock_username: str = "test_username"
    mock_response_data: dict[str, Any] = {
        "matchedUser": {
            "username": mock_username,
            "profile": {
                "countryName": "mockCountry",
                "ranking": 1,
                "userAvatar": "http://google.com",
            },
        },
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if is_valid_username else None,
    )

    # Act
    result = mock_leetcodeapi.get_user_public_profile(mock_username)

    # Assert
    if is_valid_username:
        assert result
        assert result.username == mock_username
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _USER_PROFILE_QUERY,
        user_public_profile_schema,
        {"username": mock_username},
    )


@pytest.mark.parametrize("has_recent_submissions", [True, False])
def test_get_user_recent_ac_submissions(
    mocker: MockFixture,
    mock_leetcodeapi: LeetcodeAPI,
    has_recent_submissions: bool,
) -> None:
    # Arrange
    mock_username: str = "test_username"
    mock_response_data: dict[str, Any] = {
        "recentAcSubmissionList": [
            {
                "id": "1",
                "titleSlug": "problem_1",
                "timestamp": "1681449560000",
            },
            {
                "id": "2",
                "titleSlug": "problem_2",
                "timestamp": "1681449560000",
            },
        ],
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if has_recent_submissions else None,
    )

    # Act
    result = mock_leetcodeapi.get_user_recent_ac_submissions(mock_username)

    # Assert
    if has_recent_submissions:
        assert result
        assert len(result) == len(mock_response_data["recentAcSubmissionList"])
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _USER_RECENT_AC_SUBMISSIONS_QUERY,
        user_recent_ac_submissions_schema,
        {"username": mock_username, "limit": 3},
    )


@pytest.mark.parametrize("is_valid_username", [True, False])
def test_get_user_problems_solved(
    mocker: MockFixture,
    mock_leetcodeapi: LeetcodeAPI,
    is_valid_username: bool,
) -> None:
    # Arrange
    mock_username: str = "test_username"
    mock_response_data: dict[str, Any] = {
        "matchedUser": {
            "submitStatsGlobal": {
                "acSubmissionNum": [
                    {
                        "difficulty": "All",
                        "count": 10,
                    },
                    {
                        "difficulty": "Easy",
                        "count": 6,
                    },
                    {
                        "difficulty": "Medium",
                        "count": 3,
                    },
                    {
                        "difficulty": "Hard",
                        "count": 1,
                    },
                ],
            },
        },
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if is_valid_username else None,
    )

    # Act
    result = mock_leetcodeapi.get_user_problems_solved(mock_username)

    # Assert
    if is_valid_username:
        assert result
        assert result.allProblems == 10
        assert result.hardProblems == 1
        assert result.mediumProblems == 3
        assert result.easyProblems == 6
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _USER_PROBLEMS_SOLVED_QUERY,
        user_problems_solved_schema,
        {"username": mock_username},
    )


@pytest.mark.parametrize("is_valid_problem", [True, False])
def test_get_problem_info(
    mocker: MockFixture,
    mock_leetcodeapi: LeetcodeAPI,
    is_valid_problem: bool,
) -> None:
    # Arrange
    mock_problem_slug: str = "problem_1"
    mock_response_data: dict[str, Any] = {
        "question": {
            "titleSlug": mock_problem_slug,
            "title": "Problem 1",
            "questionId": "1",
            "questionFrontendId": "1",
            "difficulty": "Easy",
        },
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if is_valid_problem else None,
    )

    # Act
    result = mock_leetcodeapi.get_problem_info(mock_problem_slug)

    # Assert
    if is_valid_problem:
        assert result
        assert result.titleSlug == mock_problem_slug
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _PROBLEM_INFO_QUERY,
        problem_info_schema,
        {"titleSlug": mock_problem_slug},
    )


@pytest.mark.parametrize("has_problems", [True, False])
def test_get_problemset_list(
    mocker: MockFixture,
    mock_leetcodeapi: LeetcodeAPI,
    has_problems: bool,
) -> None:
    # Arrange
    mock_n_problems: int = 10
    mock_response_data: dict[str, Any] = {
        "problemsetQuestionList": {
            "total": mock_n_problems,
            "questions": [
                {
                    "titleSlug": f"problem_{index}",
                    "title": f"Problem {index}",
                    "questionId": str(index),
                    "questionFrontendId": str(index),
                    "difficulty": "Easy",
                }
                for index in range(mock_n_problems)
            ],
        },
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if has_problems else None,
    )

    # Act
    result = mock_leetcodeapi.get_problemset_list()

    # Assert
    if has_problems:
        assert result
        assert result.total == len(result.questions)
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _PROBLEMSET_LIST_QUERY,
        problemset_list_schema,
        {"limit": 5000, "categorySlug": "", "filters": {}},
    )
