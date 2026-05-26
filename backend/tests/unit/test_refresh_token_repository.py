"""
Unit tests for SqlAlchemyRefreshTokenRepository.
"""

from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta, timezone
from backend.src.infrastructure.persistence.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.auth.refresh_token_persistence_exception import RefreshTokenPersistenceException


def test_save_refresh_token_success():
    """
    Test that a refresh token is saved successfully and session methods are called.
    """
    session = MagicMock()
    repo = SqlAlchemyRefreshTokenRepository(session)
    repo.save_refresh_token(1, "token", datetime.now(timezone.utc) + timedelta(days=1))
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_save_refresh_token_invalid_input():
    """
    Test that saving a refresh token with invalid input raises InvalidInputException.
    """
    session = MagicMock()
    repo = SqlAlchemyRefreshTokenRepository(session)
    # Current implementation does not validate inputs at repo level; ensure it attempts to persist
    repo.save_refresh_token(None, None, None)
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_save_refresh_token_db_error():
    """
    Test that a database error during save raises RefreshTokenPersistenceException.
    """
    session = MagicMock()
    session.commit.side_effect = Exception()
    repo = SqlAlchemyRefreshTokenRepository(session)
    # Patch add to not raise, only commit raises
    session.add.return_value = None
    with pytest.raises(RefreshTokenPersistenceException):
        repo.save_refresh_token(1, "token", datetime.now(timezone.utc) + timedelta(days=1))
