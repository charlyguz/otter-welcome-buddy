import random
from time import sleep
from typing import Any

import requests

from otter_welcome_buddy.common.utils.requests import validate_response
from otter_welcome_buddy.common.utils.types.requests import GraphqlDataRequestType


class GraphQLClient:
    """
    A client for making GraphQL requests and validating the response data against a JSON schema.
    """

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        base_sleep_seconds: float = 0.001,
        jitter_factor: float = 2,
    ):
        """
        Initialize the GraphQL client with the given URL, headers, and retry settings.

        Parameters:
            url:                The URL to send the request to.
            headers:            A dictionary of headers to include in the request.
            base_sleep_seconds: The base time that the process will wait before sending another
                                request.
            jitter_factor:      The maximum amount of jitter to apply to the backoff time.
        """
        self.base_url = url
        self.headers = headers
        # self.headers['Content-Type'] = 'application/json'
        self.retry_delay = base_sleep_seconds
        self.jitter_factor = jitter_factor

    def _sleep(self, attempt: int) -> None:
        exp_backoff_component: float = self.retry_delay * pow(2, attempt - 1)
        # Note: a uniform random will produce some bias towards a > 1 multiplier value
        jitter_multiplier: float = random.uniform(1 / self.jitter_factor, self.jitter_factor)
        sleep_seconds: float = exp_backoff_component * jitter_multiplier
        print(f"Sleeping for {round(sleep_seconds, 4)} seconds")
        sleep(sleep_seconds)

    def make_request(
        self,
        query: str,
        schema: dict[str, Any],
        variables: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any] | None:
        """
        Sends a GraphQL request to the specified URL using the specified query and variables.
        Returns the response data as a namedtuple. If the request fails, retries up to
        `max_retries` times with mixed exponential backoff and jittering.

        Parameters:
            query:          The GraphQL query string.
            variables:      A dictionary of variables to include in the request.
            max_retries:    The maximum number of retries to make if the request fails.

        Returns:
            namedtuple: A namedtuple containing the response data from the GraphQL API.

        Raises:
            requests.exceptions.RequestException:   If the request fails after the maximum
                                                    number of retries.
        """
        # Set up the request payload
        payload: GraphqlDataRequestType = {"query": query}
        if variables:
            payload["variables"] = variables

        # Send the request with retries
        for retry_count in range(1, max_retries + 1):
            try:
                # Send the request
                response = requests.post(self.base_url, json=payload, headers=self.headers)

                # If the response status code is not in the 200s range, raise an exception
                response.raise_for_status()

                # Parse the response data as JSON and process it
                response_content: dict[str, Any] = response.json()

                if "errors" in response_content:
                    print(f"Received an error from the server: {response_content['errors'][0]['message']}")
                    return None

                response_data: dict[str, Any] = response_content["data"]
                validate_response(response_data, schema)
                return response_data
            except requests.exceptions.RequestException as ex:
                print(f"Status {ex.response.status_code if ex.response else '[Undefined]'} got when making a request")

                if retry_count == max_retries:
                    # If this was the last retry, re-raise the exception
                    raise ex

                # Otherwise, wait and try again
                self._sleep(retry_count)
        return None
