"""
SQLAlchemy repository for refresh tokens.

This module provides a repository implementation for refresh token persistence using SQLAlchemy ORM.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.domain.entities.refresh_token import RefreshTokenDTO
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.refresh_token_persistence_exception import RefreshTokenPersistenceException
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
            session: SQLAlchemy session.
        """
        self._session = session

    def save_refresh_token(self, member_id: int, refresh_token: str, expires_at: datetime) -> None:
        """
        Persist a refresh token.

        Args:
            member_id: The ID of the member.
            refresh_token: The refresh token string.
            expires_at: Expiration datetime for the token.

        Raises:
            InvalidInputException: If required arguments are missing or token already exists.
            RefreshTokenPersistenceException: For database errors during persistence.
        """
        if not member_id or not refresh_token or not expires_at:
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
            logger.info("Refresh token saved (member_id=%s).", member_id)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Refresh token already exists (member_id=%s).", member_id)
            raise InvalidInputException("Refresh token already exists.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error("Failed to save refresh token (member_id=%s): %s.", member_id, str(e))
            raise RefreshTokenPersistenceException(str(e)) from e

    def get_refresh_token(self, refresh_token: str) -> RefreshTokenDTO | None:
        """
        Fetch a refresh token record.

        Args:
            refresh_token: The refresh token string to fetch.

        Returns:
            RefreshTokenDTO if found, otherwise None.

        Raises:
            InvalidInputException: If refresh_token is missing.
            RefreshTokenPersistenceException: For database errors during fetch.
        """
        if not refresh_token:
            raise InvalidInputException("refresh_token is required.")

        try:
            record = self._session.query(RefreshTokenModel).filter_by(
                refresh_token=refresh_token,
                is_revoked=False,
            ).first()

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

        except SQLAlchemyError as e:
            logger.error("Failed to fetch refresh token: %s.", str(e))
            raise RefreshTokenPersistenceException(str(e)) from e

    def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke a refresh token.

        Args:
            refresh_token: The refresh token string to revoke.

        Raises:
            InvalidInputException: If refresh_token is missing or not found.
            RefreshTokenPersistenceException: For database errors during revocation.
        """
        if not refresh_token:
            raise InvalidInputException("refresh_token is required.")

        try:
            updated = self._session.query(RefreshTokenModel).filter_by(
                refresh_token=refresh_token
            ).update({"is_revoked": True})

            if not updated:
                logger.warning("Refresh token not found for revocation.")
                raise InvalidInputException("Refresh token not found.")

            self._session.commit()
            logger.info("Refresh token revoked successfully.")

        except InvalidInputException:
            raise
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error("Failed to revoke refresh token: %s.", str(e))
            raise RefreshTokenPersistenceException(str(e)) from e

    def delete_expired(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            The number of deleted refresh tokens.

        Raises:
            RefreshTokenPersistenceException: For database errors during deletion.
        """
        try:
            deleted = self._session.query(RefreshTokenModel).filter(
                RefreshTokenModel.expires_at < datetime.now(timezone.utc)
            ).delete(synchronize_session=False)

            self._session.commit()
            logger.info("Deleted %d expired refresh tokens.", deleted)
            return deleted

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.error("Failed to delete expired refresh tokens: %s.", str(e))
            raise RefreshTokenPersistenceException(str(e)) from e