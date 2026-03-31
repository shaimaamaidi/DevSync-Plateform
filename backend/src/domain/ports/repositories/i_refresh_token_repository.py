"""
SQLAlchemy repository for ClickUp spaces.

This module provides a repository implementation for ClickUp space persistence using SQLAlchemy ORM.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from backend.src.domain.entities.refresh_token import RefreshTokenDTO


class IRefreshTokenRepository(ABC):
    """
    Define persistence operations for refresh tokens.
    """
    @abstractmethod
    def save_refresh_token(self, member_id: int, refresh_token: str, expires_at: datetime) -> None:
        """
        Persist a refresh token.

        Args:
            member_id (int): ID of the member.
            refresh_token (str): The refresh token string.
            expires_at (datetime): Expiration datetime.

        Returns:
            None: This method does not return a value; it saves the token in the persistence layer.
        """
        pass

    @abstractmethod
    def get_refresh_token(self, refresh_token: str) -> RefreshTokenDTO:
        """
        Fetch a refresh token record.

        Args:
            refresh_token (str): The refresh token string.

        Returns:
            RefreshTokenDTO: The refresh token record.
        """
        pass

    @abstractmethod
    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke a refresh token.

        Args:
            refresh_token (str): The refresh token string.

        Returns:
            None: This method does not return a value; it revokes the token in the persistence layer.
        """
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            int: Number of deleted tokens.
        """
        pass