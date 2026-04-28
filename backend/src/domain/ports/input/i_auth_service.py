"""
Service port for authentication operations.

This module defines the IAuthService interface, which specifies authentication-related
use cases such as login, token refresh, and logout.

It acts as a contract for application-level authentication services responsible for:
- Verifying member credentials
- Issuing and refreshing JWT tokens
- Revoking refresh tokens during logout
"""

from abc import ABC, abstractmethod

from backend.src.domain.entities.member import MemberAuthDTO, MemberTokensDTO


class IAuthService(ABC):
    """
    Define authentication service behavior required by the application.

    This interface represents the contract for handling authentication workflows,
    including login, token refresh, and logout operations. It abstracts the underlying
    authentication mechanism and token management strategy.
    """

    @abstractmethod
    def login(self, member: MemberAuthDTO) -> MemberTokensDTO:
        """
        Authenticate a member and return access and refresh tokens.

        Args:
            member (MemberAuthDTO): Member authentication payload (mail and password).

        Returns:
            MemberTokensDTO: DTO containing access and refresh tokens.
        """
        pass

    @abstractmethod
    def refresh(self, refresh_token: str) -> MemberTokensDTO:
        """
        Issue new tokens from a valid refresh token.

        Args:
            refresh_token (str): The refresh token string.

        Returns:
            MemberTokensDTO: DTO containing new access and refresh tokens.
        """
        pass

    @abstractmethod
    def logout(self, refresh_token: str) -> None:
        """
        Revoke a refresh token (logout the member).

        Args:
            refresh_token (str): The refresh token to revoke.

        Returns:
            None: Operation revokes the refresh token (logout).
        """
        pass