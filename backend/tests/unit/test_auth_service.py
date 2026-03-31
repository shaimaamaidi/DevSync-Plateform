"""Unit tests for AuthService."""

from unittest.mock import MagicMock
import pytest
from backend.src.application.services.auth_service import AuthService
from backend.src.domain.entities.member import MemberAuthDTO, MemberTokensDTO
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.invalid_token_exception import InvalidTokenException


def test_login_success() -> None:
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()
    member_repo.verify_credentials.return_value = True
    jwt_handler.create_tokens.return_value = MemberTokensDTO(access_token="access", refresh_token="refresh")
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)

    credentials = MemberAuthDTO(mail="user@mail.com", password="pass")
    result = service.login(credentials)

    member_repo.verify_credentials.assert_called_once_with(credentials)
    jwt_handler.create_tokens.assert_called_once()
    assert result.access_token == "access"
    assert result.refresh_token == "refresh"


def test_login_invalid_credentials() -> None:
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()
    member_repo.verify_credentials.return_value = False
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)

    credentials = MemberAuthDTO(mail="user@mail.com", password="wrong")
    with pytest.raises(InvalidInputException):
        service.login(credentials)


def test_refresh_invalid_token() -> None:
    member_repo = MagicMock()
    jwt_handler = MagicMock()
    refresh_token_repo = MagicMock()
    jwt_handler.verify_refresh_token.side_effect = InvalidTokenException()
    service = AuthService(member_repo, jwt_handler, refresh_token_repo)

    with pytest.raises(InvalidTokenException):
        service.refresh("badtoken")
