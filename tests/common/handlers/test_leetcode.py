from typing import Any

import pytest
from jsonschema import ValidationError
from pytest_mock import MockFixture
from requests import RequestException

from otter_welcome_buddy.common.handlers.graphql import GraphQLClient
from otter_welcome_buddy.common.handlers.leetcode import _USER_PROBLEM_SOLVED
from otter_welcome_buddy.common.handlers.leetcode import _USER_PROFILE_QUERY
from otter_welcome_buddy.common.handlers.leetcode import _USER_RECENT_AC_SUBMISSIONS
from otter_welcome_buddy.common.handlers.leetcode import LeetcodeAPI
from otter_welcome_buddy.common.json_schemas.leetcode_schemas import user_problem_solved_schema
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
        _USER_RECENT_AC_SUBMISSIONS,
        user_recent_ac_submissions_schema,
        {"username": mock_username, "limit": 3},
    )


@pytest.mark.parametrize("is_valid_username", [True, False])
def test_get_user_problem_solved(
    mocker: MockFixture,
    mock_leetcodeapi: LeetcodeAPI,
    is_valid_username: bool,
) -> None:
    # Arrange
    mock_username: str = "test_username"
    mock_problem_slug: str = "problem_1"
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
        "question": {
            "titleSlug": mock_problem_slug,
            "questionId": "1",
            "difficulty": "Easy",
        },
    }

    mocked_fetch_request = mocker.patch.object(
        LeetcodeAPI,
        "_fetch_request",
        return_value=mock_response_data if is_valid_username else None,
    )

    # Act
    result = mock_leetcodeapi.get_user_problem_solved(mock_username, mock_problem_slug)

    # Assert
    if is_valid_username:
        assert result
        assert result.question.titleSlug == mock_problem_slug
        assert result.nProblems == 10
    else:
        assert result is None
    mocked_fetch_request.assert_called_once_with(
        _USER_PROBLEM_SOLVED,
        user_problem_solved_schema,
        {"username": mock_username, "titleSlug": mock_problem_slug},
    )
