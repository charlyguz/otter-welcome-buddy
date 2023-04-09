from typing import Any

import jsonschema


def validate_response(response_data: dict[str, Any], schema: dict[str, Any]) -> None:
    """
    Validates the response data from the GraphQL API using the specified JSON schema.

    Parameters:
        response_data (dict): The response data from the GraphQL API.
        schema (dict): The JSON schema to validate the response data against.

    Raises:
        jsonschema.ValidationError: If the response data fails validation against the schema.
    """
    jsonschema.validate(response_data, schema)
