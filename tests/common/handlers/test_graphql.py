import random
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from pytest_mock import MockFixture

from otter_welcome_buddy.common.handlers.graphql import GraphQLClient


@pytest.fixture
def mock_graphqlclient() -> GraphQLClient:
    mock_graphqlclient = GraphQLClient("http://example.com/graphql")
    return mock_graphqlclient


@pytest.fixture
def mock_query() -> str:
    mock_query = "query { my_field }"
    return mock_query


@pytest.fixture
def mock_schema() -> dict[str, Any]:
    mock_schema = {
        "type": "object",
        "properties": {
            "my_field": {
                "type": "string",
            },
        },
    }
    return mock_schema


def test__sleep(mocker: MockFixture, mock_graphqlclient: GraphQLClient) -> None:
    # Arrange
    mocked_random = mocker.patch.object(random, "uniform", return_value=1)
    mocked_sleep = mocker.patch("otter_welcome_buddy.common.handlers.graphql.sleep")

    # Act
    mock_graphqlclient._sleep(1)

    # Assert
    mocked_random.assert_called_once_with(0.5, 2)
    mocked_sleep.assert_called_once_with(0.001)


def test_make_request_returns_valid_response_data(
    mocker: MockFixture,
    mock_graphqlclient: GraphQLClient,
    mock_query: str,
    mock_schema: dict[str, Any],
) -> None:
    # Arrange
    mock_response_data: dict[str, Any] = {"data": {"my_field": "my_value"}}
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None

    mocked_post = mocker.patch.object(requests, "post", return_value=mock_response)

    # Act
    response_data = mock_graphqlclient.make_request(mock_query, mock_schema)

    # Assert
    assert response_data == mock_response_data["data"]
    mocked_post.assert_called_once()


def test_make_request_raises_exception_on_failure(
    mocker: MockFixture,
    mock_graphqlclient: GraphQLClient,
    mock_query: str,
    mock_schema: dict[str, Any],
) -> None:
    # Arrange
    mock_max_retries: int = 3
    mock_exception: Exception = requests.exceptions.RequestException("Error")

    mocked_post = mocker.patch.object(requests, "post", side_effect=mock_exception)

    # Act
    with pytest.raises(requests.exceptions.RequestException) as ex:
        mock_graphqlclient.make_request(mock_query, mock_schema, max_retries=mock_max_retries)

    # Assert
    assert ex.value == mock_exception
    mocked_post.assert_called()
    assert mocked_post.call_count == mock_max_retries


def test_make_request_returns_none_on_server_error(
    mocker: MockFixture,
    mock_graphqlclient: GraphQLClient,
    mock_query: str,
    mock_schema: dict[str, Any],
) -> None:
    # Arrange
    mock_response_data: dict[str, Any] = {"errors": [{"message": "Server error"}]}
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status.return_value = None

    mocked_post = mocker.patch.object(requests, "post", return_value=mock_response)

    # Act
    response_data = mock_graphqlclient.make_request(mock_query, mock_schema)

    # Assert
    assert response_data is None
    mocked_post.assert_called_once()
