"""
HTTP client for ClickUp API interactions.

This module defines the ClickUpHttpClient class, which provides a low-level
transport layer for interacting with the ClickUp v2 REST API. It is responsible
for executing HTTP requests (GET, POST, PUT) and translating HTTP errors into
domain-specific exceptions.

This client contains no business logic and is used by infrastructure services.
"""

import logging
import os
import requests
from typing import Any

from dotenv import load_dotenv

from backend.src.domain.exceptions.clickup.clickup_api_exception import ClickUpApiException
from backend.src.domain.exceptions.clickup.clickup_authentication_exception import ClickUpAuthenticationException
from backend.src.domain.exceptions.clickup.clickup_resource_not_found_exception import ClickUpResourceNotFoundException
from backend.src.domain.exceptions.clickup.missing_clickup_config_exception import MissingClickUpConfigException


logger = logging.getLogger(__name__)


class ClickUpHttpClient:
    """
    Base HTTP client for ClickUp API communication.

    This class centralizes:
    - Authentication via environment variables
    - HTTP request execution (GET, POST, PUT)
    - Error handling and mapping to domain exceptions

    Attributes:
        BASE_URL (str): Base URL for ClickUp API.
        _headers (dict): HTTP headers including authentication token.
    """

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        """
        Initialize the ClickUp HTTP client.

        Loads environment variables, validates the presence of the ClickUp API token,
        and prepares HTTP headers for authenticated requests.

        Raises:
            MissingClickUpConfigException: If the API token is missing from environment.
        """
        load_dotenv()

        api_token = os.getenv("CLICKUP_API_TOKEN")
        if not api_token:
            raise MissingClickUpConfigException(
                "CLICKUP_API_TOKEN is missing from environment variables."
            )

        self._headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
        }


    def get(self, endpoint: str) -> Any:
        """
        Send a GET request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.

        Returns:
            Parsed JSON response.
        """
        logger.info("GET %s", endpoint)

        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=self._headers)
        self._handle_response(response)
        return response.json()

    def post(self, endpoint: str, payload: dict) -> Any:
        """
        Send a POST request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.
        """
        logger.info("POST %s", endpoint)

        response = requests.post(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )
        self._handle_response(response)
        return response.json()

    def post_raw(self, endpoint: str, payload: dict) -> requests.Response:
        """
        Send a POST request and return the raw HTTP response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw HTTP response object.
        """
        logger.info("POST (raw) %s", endpoint)

        return requests.post(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )

    def put(self, endpoint: str, payload: dict) -> Any:
        """
        Send a PUT request to ClickUp API.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Parsed JSON response.
        """
        logger.info("PUT %s", endpoint)

        response = requests.put(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )
        self._handle_response(response)
        return response.json()

    def put_raw(self, endpoint: str, payload: dict) -> requests.Response:
        """
        Send a PUT request and return the raw HTTP response.

        Args:
            endpoint: API endpoint path starting with '/'.
            payload: JSON payload to send.

        Returns:
            Raw HTTP response object.
        """
        logger.info("PUT (raw) %s", endpoint)

        return requests.put(
            f"{self.BASE_URL}{endpoint}",
            json=payload,
            headers=self._headers
        )

    @staticmethod
    def _handle_response(response: requests.Response) -> None:
        """
        Handle HTTP responses and map errors to domain exceptions.

        Args:
            response: HTTP response returned by ClickUp API.

        Raises:
            ClickUpAuthenticationException: If status code is 401.
            ClickUpResourceNotFoundException: If status code is 404.
            ClickUpApiException: For all other non-success responses.
        """
        if response.status_code == 401:
            raise ClickUpAuthenticationException(
                f"Invalid or expired token — {response.text}"
            )

        if response.status_code == 404:
            raise ClickUpResourceNotFoundException(
                f"Resource not found: {response.url} — {response.text}"
            )

        if not response.ok:
            raise ClickUpApiException(
                f"ClickUp API error ({response.status_code}) — {response.text}"
            )