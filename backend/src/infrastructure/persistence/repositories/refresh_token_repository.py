"""
SQLAlchemy repository for refresh tokens.

This module provides a repository implementation for refresh token persistence using SQLAlchemy ORM.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.domain.entities.refresh_token import RefreshTokenDTO
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.auth.refresh_token_persistence_exception import RefreshTokenPersistenceException
from backend.src.domain.ports.repositories.i_refresh_token_repository import IRefreshTokenRepository
from backend.src.infrastructure.persistence.models.refresh_token_model import RefreshTokenModel


logger = logging.getLogger(__name__)


class SqlAlchemyRefreshTokenRepository(IRefreshTokenRepository):
    """
    SQLAlchemy implementation of IRefreshTokenRepository for refresh token persistence.

    This repository handles CRUD operations for refresh tokens using SQLAlchemy ORM.

    Attributes:
        _session (Session): SQLAlchemy session for database operations.
    """

    def __init__(self, session):
        """
        Initialize the repository with a session.

        Args:
            session (Session): SQLAlchemy session.
        """
        self._session = session

    def save_refresh_token(self, member_id: int, refresh_token: str, expires_at: datetime) -> None:
        """
        Persist a refresh token.

        Args:
            member_id (int): The ID of the member.
            refresh_token (str): The refresh token string.
            expires_at (datetime): Expiration datetime for the token.

        Returns:
            None: This method does not return a value; it saves the token in the persistence layer.

        Raises:
            InvalidInputException: If required arguments are missing.
            InvalidInputException: If token already exists (IntegrityError triggers rollback).
            RefreshTokenPersistenceException: For other database errors (rollback performed).
        """
        logger.info("Starting saving refresh token (member_id=%s).", member_id)

        if not member_id or not refresh_token or not expires_at:
            logger.error(
                "Save failed: Missing arguments (member_id=%s, has_token=%s, has_expiry=%s)",
                member_id,
                bool(refresh_token),
                bool(expires_at),
            )
            raise InvalidInputException("member_id, refresh_token and expires_at are required.")

        try:
            self._session.query(RefreshTokenModel).filter_by(
                member_id=member_id, is_revoked=False
            ).update({"is_revoked": True})

            record = RefreshTokenModel(
                member_id=member_id,
                refresh_token=refresh_token,
                expires_at=expires_at,
                is_revoked=False,
            )

            self._session.add(record)
            self._session.commit()

            logger.info("Refresh token saved successfully (member_id=%s, expires_at=%s).",
            member_id,
                expires_at
            )

        except IntegrityError as e:
            self._session.rollback()
            logger.exception("Integrity error: token already exists (member_id=%s).", member_id)
            raise InvalidInputException("Refresh token already exists.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to save refresh token (member_id=%s).", member_id)
            raise RefreshTokenPersistenceException(str(e)) from e
        except Exception as e:
            self._session.rollback()
            logger.exception("Unexpected error while saving refresh token (member_id=%s).", member_id)
            raise RefreshTokenPersistenceException(str(e)) from e

    def get_refresh_token(self, refresh_token: str) -> RefreshTokenDTO | None:
        """
        Fetch a refresh token record.

        Args:
            refresh_token (str): The refresh token string to fetch.

        Returns:
            RefreshTokenDTO if found, otherwise None.

        Raises:
            InvalidInputException: If refresh_token is missing.
            RefreshTokenPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching refresh token.")

        if not refresh_token:
            raise InvalidInputException("refresh_token is required.")

        try:
            record = self._session.query(RefreshTokenModel).filter_by(
                refresh_token=refresh_token,
                is_revoked=False,
            ).first()

        except SQLAlchemyError as e:
            logger.exception("Failed to fetch refresh token.")
            raise RefreshTokenPersistenceException(str(e)) from e

        if not record:
            logger.warning("Refresh token not found or already revoked.")
            return None

        return RefreshTokenDTO(
            id=record.id,
            member_id=record.member_id,
            refresh_token=record.refresh_token,
            expires_at=record.expires_at,
            is_revoked=record.is_revoked,
        )

    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke a refresh token.

        Args:
            refresh_token (str): The refresh token string to revoke.

        Returns:
            None: This method does not return a value; it revokes the token in the persistence layer.
        Raises:
            InvalidInputException: If refresh_token is missing or not found.
            RefreshTokenPersistenceException: For database errors during revocation.
        """
        logger.info("Revoking refresh token.")

        if not refresh_token:
            raise InvalidInputException("refresh_token is required.")

        try:
            updated = self._session.query(RefreshTokenModel).filter_by(
                refresh_token=refresh_token, is_revoked=False
            ).update({"is_revoked": True})

            if not updated:
                logger.warning("Refresh token not found for revocation.")
                raise InvalidInputException("Refresh token not found.")

            self._session.commit()

            logger.info("Refresh token revoked successfully.")

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to revoke refresh token.")
            raise RefreshTokenPersistenceException(str(e)) from e

    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            int: The number of deleted refresh tokens.

        Raises:
            RefreshTokenPersistenceException: For database errors during deletion.
        """
        logger.info("Deleting expired refresh tokens.")

        try:
            deleted = self._session.query(RefreshTokenModel).filter(
                RefreshTokenModel.expires_at < datetime.now(timezone.utc)
            ).delete(synchronize_session=False)

            self._session.commit()

            logger.info("Deleted %d expired refresh tokens.", deleted)

            return deleted

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to delete expired refresh tokens.")
            raise RefreshTokenPersistenceException(str(e)) from e