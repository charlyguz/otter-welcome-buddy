from typing import Any

import jsonschema
import pytest
from pytest_mock import MockFixture

from otter_welcome_buddy.common.utils.http_requests import validate_response


@pytest.fixture
def mock_response() -> dict[str, Any]:
    mock_response = {
        "data": {
            "user": {
                "id": 123,
                "name": "John Smith",
                "email": "john@email.com",
            },
        },
    }
    return mock_response


@pytest.fixture
def mock_schema() -> dict[str, Any]:
    mock_schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "number"},
                            "name": {"type": "string"},
                        },
                        "required": ["id", "name"],
                    },
                },
                "required": ["user"],
            },
        },
        "required": ["data"],
    }
    return mock_schema


def test_valid_response(mocker: MockFixture, mock_response: dict[str, Any], mock_schema: dict[str, Any]) -> None:
    # Arrange
    mocked_jsonschema_validate = mocker.patch.object(jsonschema, "validate")

    # Act
    validate_response(mock_response, mock_schema)

    # Assert
    mocked_jsonschema_validate.assert_called_once()


def test_invalid_response(mocker: MockFixture, mock_schema: dict[str, Any]) -> None:
    # Arrange
    mock_response = {"data": {"user": {"id": 123}}}
    mock_exception = jsonschema.ValidationError("Invalid response")

    mocked_jsonschema_validate = mocker.patch.object(jsonschema, "validate", side_effect=mock_exception)

    # Act
    with pytest.raises(jsonschema.ValidationError) as ex:
        validate_response(mock_response, mock_schema)

    # Assert
    mocked_jsonschema_validate.assert_called_once()
    assert ex.value == mock_exception


def test_invalid_schema(mocker: MockFixture, mock_response: dict[str, Any]) -> None:
    # Arrange
    mock_schema = {"type": "object", "properties": {"data": {"type": "array"}}}
    mock_exception = jsonschema.SchemaError("Invalid schema")

    mocked_jsonschema_validate = mocker.patch.object(jsonschema, "validate", side_effect=mock_exception)

    # Act
    with pytest.raises(jsonschema.SchemaError) as ex:
        validate_response(mock_response, mock_schema)

    # Assert
    mocked_jsonschema_validate.assert_called_once()
    assert ex.value == mock_exception
