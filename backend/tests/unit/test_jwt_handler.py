"""
Unit tests for JWTHandler behaviour: token creation and verification.
"""

import os
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from backend.src.infrastructure.security.jwt_handler import JWTHandler
from backend.src.domain.exceptions.auth.invalid_token_exception import InvalidTokenException
from backend.src.domain.exceptions.base.app_exception import AppException


def _install_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-123")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5")
    monkeypatch.setenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")


def test_create_and_verify_access_token_roundtrip(monkeypatch) -> None:
    """create_access_token should produce a token that verify_token accepts."""
    _install_env(monkeypatch)

    handler = JWTHandler()

    token = handler.create_access_token({"sub": "member-1", "mail": "a@b.c"})

    payload = handler.verify_token(token)

    assert payload["sub"] == "member-1"
    assert payload["mail"] == "a@b.c"


def test_verify_token_rejects_missing_claims(monkeypatch) -> None:
    """Tokens missing required claims should raise InvalidTokenException."""
    _install_env(monkeypatch)

    secret = os.getenv("JWT_SECRET_KEY")

    # encode a token without the `mail` claim but with an exp in the future
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    token = jwt.encode({"sub": "m-2", "exp": exp}, secret, algorithm="HS256")

    handler = JWTHandler()

    # The implementation wraps internal InvalidTokenException into AppException
    with pytest.raises(AppException):
        handler.verify_token(token)


def test_verify_token_rejects_expired_token(monkeypatch) -> None:
    """Expired tokens should raise InvalidTokenException."""
    _install_env(monkeypatch)

    secret = os.getenv("JWT_SECRET_KEY")

    exp = datetime.now(timezone.utc) - timedelta(seconds=1)
    token = jwt.encode({"sub": "m-3", "mail": "x@y.z", "exp": exp}, secret, algorithm="HS256")

    handler = JWTHandler()

    with pytest.raises(InvalidTokenException):
        handler.verify_token(token)
"""
Unit tests for JWTHandler.
"""

import pytest
import os
from backend.src.infrastructure.security.jwt_handler import JWTHandler
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.auth.invalid_token_exception import InvalidTokenException


def test_missing_env_variables(monkeypatch):
    """
    Test that JWTHandler raises an exception if required environment variables are missing.
    """
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    monkeypatch.delenv("REFRESH_TOKEN_EXPIRE_DAYS", raising=False)
    monkeypatch.setattr(
        "backend.src.infrastructure.security.jwt_handler.load_dotenv",
        lambda *args, **kwargs: None
    )

    with pytest.raises(MissingEnvVariableException):
        JWTHandler()


def test_invalid_token():
    """
    Test that JWTHandler raises InvalidTokenException for an invalid token string.
    """
    os.environ["JWT_SECRET_KEY"] = "test"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "1"
    os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "1"
    handler = JWTHandler()
    with pytest.raises(InvalidTokenException):
        handler.verify_token("invalid.token.here")
