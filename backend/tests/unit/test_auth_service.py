"""
Unit tests for AuthService.
"""

from unittest.mock import MagicMock, patch
import pytest
from backend.src.application.services.auth_service import AuthService
from backend.src.domain.entities.member import MemberAuthDTO
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.auth.invalid_token_exception import InvalidTokenException


def test_login_success() -> None:
    """
    Test successful login returns access and refresh tokens and calls all dependencies.
    """
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()

    credentials_obj = MagicMock()
    credentials_obj.hashed_password = "hashed"
    credentials_obj.id = 1
    credentials_obj.mail = "user@mail.com"
    member_repo.find_credentials_by_mail.return_value = credentials_obj
    jwt_handler.create_access_token.return_value = "access"
    jwt_handler.create_refresh_token.return_value = ("refresh", "expiry")
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)
    credentials = MemberAuthDTO(mail="user@mail.com", password="pass")

    with patch("backend.src.application.services.auth_service.verify_password", return_value=True):
        result = service.login(credentials)

    member_repo.find_credentials_by_mail.assert_called_once_with("user@mail.com")
    jwt_handler.create_access_token.assert_called_once()
    jwt_handler.create_refresh_token.assert_called_once()
    refresh_token_repo.save_refresh_token.assert_called_once()
    assert result.access_token == "access"
    assert result.refresh_token == "refresh"

def test_login_invalid_credentials() -> None:
    """
    Test login with invalid credentials raises InvalidInputException.
    """
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()
    credentials_obj = MagicMock()
    credentials_obj.hashed_password = "hashed"
    credentials_obj.id = 1
    credentials_obj.mail = "user@mail.com"
    member_repo.find_credentials_by_mail.return_value = credentials_obj
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)
    credentials = MemberAuthDTO(mail="user@mail.com", password="wrong")

    with patch("backend.src.application.services.auth_service.verify_password", return_value=False):
        with pytest.raises(InvalidInputException):
            service.login(credentials)


def test_refresh_invalid_token() -> None:
    """
    Test that refreshing with an invalid token raises InvalidTokenException.
    """
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()
    jwt_handler.verify_refresh_token.side_effect = InvalidTokenException()
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)

    with pytest.raises(InvalidTokenException):
        service.refresh("badtoken")
