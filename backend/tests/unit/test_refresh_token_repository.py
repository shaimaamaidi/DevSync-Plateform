"""Unit tests for SqlAlchemyRefreshTokenRepository."""

from unittest.mock import MagicMock
import pytest
from datetime import datetime, timedelta, timezone
from backend.src.infrastructure.persistence.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.refresh_token_persistence_exception import RefreshTokenPersistenceException


def test_save_refresh_token_success():
    session = MagicMock()
    repo = SqlAlchemyRefreshTokenRepository(session)
    repo.save_refresh_token(1, "token", datetime.now(timezone.utc) + timedelta(days=1))
    session.add.assert_called_once()
    session.commit.assert_called_once()


def test_save_refresh_token_invalid_input():
    session = MagicMock()
    repo = SqlAlchemyRefreshTokenRepository(session)
    with pytest.raises(InvalidInputException):
        repo.save_refresh_token(None, None, None)


def test_save_refresh_token_db_error():
    session = MagicMock()
    session.commit.side_effect = Exception()
    repo = SqlAlchemyRefreshTokenRepository(session)
    with pytest.raises(RefreshTokenPersistenceException):
        repo.save_refresh_token(1, "token", datetime.now(timezone.utc) + timedelta(days=1))
