"""
Authentication service module.

This module provides the AuthService class, which handles authentication use cases such as login, token refresh, and logout for members.
It coordinates member credential verification, JWT token management, and refresh token persistence.

Classes:
    AuthService: Main service for authentication logic and token lifecycle management.
"""

import logging
from datetime import datetime, timezone

from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.domain.ports.repositories.i_refresh_token_repository import IRefreshTokenRepository
from backend.src.domain.ports.services.i_jwt_handler import IJWTHandler
from backend.src.domain.entities.member import MemberAuthDTO, MemberTokensDTO
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.invalid_token_exception import InvalidTokenException
from backend.src.shared.helpers.password_helper import verify_password


logger = logging.getLogger(__name__)


class AuthService:
    """
    Application service for authentication use cases: login, refresh, logout.

    Coordinates authentication logic, token management, and member credential verification.

    Attributes:
        _repo (IMemberRepository): Persistence port for member credentials.
        _jwt_handler (IJWTHandler): JWT handler service port.
        _refresh_token_repo (IRefreshTokenRepository): Persistence port for refresh tokens.
    """

    def __init__(
        self,
        member_repository: IMemberRepository,
        jwt_handler: IJWTHandler,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        """
        Initialize the AuthService with required repositories and handlers.

        Args:
            member_repository (IMemberRepository): Member repository port.
            jwt_handler (IJWTHandler): JWT handler service port.
            refresh_token_repository (IRefreshTokenRepository): Refresh token repository port.
        """
        self._repo = member_repository
        self._jwt_handler = jwt_handler
        self._refresh_token_repo = refresh_token_repository

    def login(self, member: MemberAuthDTO) -> MemberTokensDTO:
        """
        Authenticate a member and return access and refresh tokens.

        Args:
            member (MemberAuthDTO): Member authentication payload (mail and password).

        Returns:
            MemberTokensDTO: DTO containing access and refresh tokens.

        Raises:
            InvalidInputException: If mail or password is missing/invalid.
        """
        logger.info(
            "Login attempt started for member: mail=%s.",
            member.mail
        )

        if not member.mail or not member.password:
            logger.warning("Mail and password are required.")
            raise InvalidInputException("Mail and password are required.")

        credentials = self._repo.find_credentials_by_mail(member.mail)

        if not verify_password(member.password, credentials.hashed_password):
            logger.warning("Invalid password attempt (mail=%s).", member.mail)
            raise InvalidInputException("Invalid mail or password.")

        data = {"sub": str(credentials.id), "mail": credentials.mail}
        access_token = self._jwt_handler.create_access_token(data=data)
        refresh_token, expires_at = self._jwt_handler.create_refresh_token(data=data)

        self._refresh_token_repo.save_refresh_token(credentials.id, refresh_token, expires_at)

        logger.info("Member logged in successfully (id=%s).", credentials.id)

        return MemberTokensDTO(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> MemberTokensDTO:
        """
        Issue new tokens from a valid refresh token.

        Args:
            refresh_token (str): The refresh token string.

        Returns:
            MemberTokensDTO: DTO containing new access and refresh tokens.

        Raises:
            InvalidInputException: If refresh token is missing.
            InvalidTokenException: If the token is invalid, expired, or revoked.
        """
        logger.info(
            "Token refresh attempt started: refresh_token=%s.",
            refresh_token[:8] + "..." if refresh_token else None
        )

        if not refresh_token:
            logger.warning("Refresh token is required.")
            raise InvalidInputException("Refresh token is required.")

        payload = self._jwt_handler.verify_token(refresh_token)

        if payload.get("type") != "refresh":
            logger.warning("Wrong token type used for refresh.")
            raise InvalidTokenException("Invalid token type.")

        if not payload.get("sub") or not payload.get("mail"):
            logger.warning("Token missing required claims.")
            raise InvalidTokenException("Token missing required claims.")

        record = self._refresh_token_repo.get_refresh_token(refresh_token)

        if not record:
            logger.warning("Refresh token not found or already revoked.")
            raise InvalidTokenException("Refresh token not found or already revoked.")

        if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            logger.warning("Refresh token expired (member_id=%s).", record.member_id)
            self._refresh_token_repo.revoke_refresh_token(refresh_token)
            raise InvalidTokenException("Refresh token has expired.")

        member = self._repo.find_by_id(record.member_id)
        if not member:
            logger.warning("Member not found during token refresh (id=%s).", record.member_id)
            self._refresh_token_repo.revoke_refresh_token(refresh_token)
            raise InvalidTokenException("Member does not exist.")

        self._refresh_token_repo.revoke_refresh_token(refresh_token)

        data = {"sub": payload["sub"], "mail": payload["mail"]}
        new_access_token = self._jwt_handler.create_access_token(data=data)
        new_refresh_token, expires_at = self._jwt_handler.create_refresh_token(data=data)

        self._refresh_token_repo.save_refresh_token(record.member_id, new_refresh_token, expires_at)

        logger.info("Tokens refreshed successfully (member_id=%s).", record.member_id)

        return MemberTokensDTO(access_token=new_access_token, refresh_token=new_refresh_token)

    def logout(self, refresh_token: str) -> None:
        """
        Revoke a refresh token (logout the member).

        Args:
            refresh_token (str): The refresh token to revoke.

        Returns:
            None: Operation revokes the refresh token (logout).

        Raises:
            InvalidInputException: If refresh token is missing or not found.
        """
        logger.info(
            "Logout attempt started for refresh_token=%s.",
            refresh_token[:8] + "..." if refresh_token else None
        )

        if not refresh_token:
            logger.warning("Refresh token is required.")
            raise InvalidInputException("Refresh token is required.")

        self._refresh_token_repo.revoke_refresh_token(refresh_token)

        logger.info("Member logged out successfully.")