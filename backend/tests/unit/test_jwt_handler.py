"""Unit tests for JWTHandler."""

import os
import pytest
from backend.src.infrastructure.security.jwt_handler import JWTHandler
from backend.src.domain.exceptions.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.invalid_token_exception import InvalidTokenException


def test_missing_env_variables(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    monkeypatch.delenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", raising=False)
    with pytest.raises(MissingEnvVariableException):
        JWTHandler()


def test_invalid_token():
    handler = JWTHandler()
    with pytest.raises(InvalidTokenException):
        handler.verify_access_token("invalid.token.here")
