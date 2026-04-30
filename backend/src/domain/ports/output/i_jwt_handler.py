"""
Port for JWT token operations.

This module defines the IJWTHandler interface, which specifies operations for creating,
signing, and verifying JWT tokens used for authentication and authorization.
"""

from datetime import datetime
from abc import ABC, abstractmethod


class IJWTHandler(ABC):
    """
    Define operations for creating and verifying JWT tokens.

    This interface represents the contract for JWT handling, including generation of access
    and refresh tokens as well as verification and decoding of existing tokens.
    """

    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        """
        Generate a JWT access token.

        Args:
            data (dict): Claims to encode in the token (e.g., user id, email).

        Returns:
            str: Encoded JWT access token.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict) -> tuple[str, datetime]:
        """
        Generate a JWT refresh token and its expiration time.

        Args:
            data (dict): Claims to encode in the token.

        Returns:
            tuple[str, datetime]: Refresh token and its expiration datetime.
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        """
        Verify and decode a JWT token.

        Args:
            token (str): Encoded JWT token string.

        Returns:
            dict: Decoded token claims if valid.
        """
        pass