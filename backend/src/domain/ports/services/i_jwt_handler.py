"""
Port for JWT token operations.

This module defines the IJWTHandler interface, which specifies operations for creating and verifying JWT tokens.
"""

from datetime import datetime
from abc import ABC, abstractmethod


class IJWTHandler(ABC):
    """
    Define operations for creating and verifying JWT tokens.

    This interface specifies methods for generating access and refresh tokens, and for verifying JWT tokens.
    """
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        """
        Generate a JWT access token.

        Args:
            data: Claims to encode in the token (e.g., user id, email).

        Returns:
            str: Encoded JWT access token.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict) -> tuple[str, datetime]:
        """
        Generate a JWT refresh token and its expiration.

        Args:
            data: Claims to encode in the token.

        Returns:
            tuple[str, datetime]: The refresh token and its expiration datetime.
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.

        Args:
            token: Encoded JWT token string.

        Returns:
            dict: Decoded claims if the token is valid.
        """
        pass