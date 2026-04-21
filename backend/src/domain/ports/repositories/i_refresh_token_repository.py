"""
Repository port for refresh token persistence.

This module defines the IRefreshTokenRepository interface, which specifies persistence operations
for managing refresh tokens, including creation, retrieval, revocation, and cleanup of expired tokens.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from backend.src.domain.entities.refresh_token import RefreshTokenDTO


class IRefreshTokenRepository(ABC):
    """
    Define persistence operations for refresh tokens.

    This interface represents the contract for storing and managing refresh tokens in a persistence
    layer such as a database, including lifecycle operations like revocation and cleanup.
    """

    @abstractmethod
    def save_refresh_token(
        self,
        member_id: int,
        refresh_token: str,
        expires_at: datetime,
    ) -> None:
        """
        Persist a refresh token.

        Args:
            member_id (int): Identifier of the member owning the token.
            refresh_token (str): Refresh token string.
            expires_at (datetime): Expiration datetime of the token.

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_refresh_token(self, refresh_token: str) -> RefreshTokenDTO:
        """
        Retrieve a refresh token record.

        Args:
            refresh_token (str): Refresh token string.

        Returns:
            RefreshTokenDTO: Refresh token data.
        """
        pass

    @abstractmethod
    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke a refresh token.

        Args:
            refresh_token (str): Refresh token string to revoke.

        Returns:
            None
        """
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            int: Number of deleted expired tokens.
        """
        pass