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
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    monkeypatch.delenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", raising=False)
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
