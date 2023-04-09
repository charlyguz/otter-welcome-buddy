from typing import Any
from typing import TypedDict

from typing_extensions import NotRequired


class GraphqlDataRequestType(TypedDict):
    """Data format to send the request to GraphQL"""

    query: str
    variables: NotRequired[dict[str, Any]]
