"""
Unit tests for MySQLConnector.
"""

import os
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.src.domain.exceptions.database.database_connection_exception import DatabaseConnectionException
from backend.src.domain.exceptions.database.database_initialization_exception import DatabaseInitializationException
from backend.src.domain.exceptions.database.database_session_exception import DatabaseSessionException
from backend.src.infrastructure.persistence import mysql_connector
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector


def _set_env(monkeypatch) -> None:
    monkeypatch.setenv("MYSQL_USER", "u")
    monkeypatch.setenv("MYSQL_PASSWORD", "p")
    monkeypatch.setenv("MYSQL_HOST", "h")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DB", "db")


def test_mysql_connector_missing_env_raises(monkeypatch) -> None:
    """
    Missing env vars should raise DatabaseInitializationException.
    """
    for key in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DB"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(DatabaseInitializationException):
        MySQLConnector()


def test_mysql_connector_connect_creates_engine(monkeypatch) -> None:
    """
    Connect should create engine and session factory.
    """
    _set_env(monkeypatch)

    engine = object()
    session_factory = object()

    monkeypatch.setattr(mysql_connector, "create_engine", lambda *_args, **_kwargs: engine)
    monkeypatch.setattr(mysql_connector, "sessionmaker", lambda **_kwargs: session_factory)

    connector = MySQLConnector()
    result_engine, result_session = connector.connect()

    assert result_engine is engine
    assert result_session is session_factory


def test_mysql_connector_connect_wraps_error(monkeypatch) -> None:
    """
    Connect should wrap SQLAlchemyError into DatabaseConnectionException.
    """
    _set_env(monkeypatch)

    def _boom(*_args, **_kwargs):
        raise SQLAlchemyError("fail")

    monkeypatch.setattr(mysql_connector, "create_engine", _boom)

    connector = MySQLConnector()

    with pytest.raises(DatabaseConnectionException):
        connector.connect()


def test_mysql_connector_get_session_calls_connect(monkeypatch) -> None:
    """
    get_session should call connect if Session not initialized.
    """
    _set_env(monkeypatch)

    connector = MySQLConnector()

    session_obj = object()
    connector.connect = MagicMock()
    connector.Session = MagicMock(return_value=session_obj)

    result = connector.get_session()

    connector.connect.assert_not_called()
    assert result is session_obj


def test_mysql_connector_get_session_wraps_error(monkeypatch) -> None:
    """
    get_session should wrap unexpected errors into DatabaseSessionException.
    """
    _set_env(monkeypatch)

    connector = MySQLConnector()
    connector.Session = MagicMock(side_effect=RuntimeError("fail"))

    with pytest.raises(DatabaseSessionException):
        connector.get_session()


def test_mysql_connector_create_db_if_not_exists_wraps_error(monkeypatch) -> None:
    """
    create_db_if_not_exists should wrap SQLAlchemyError into DatabaseInitializationException.
    """
    _set_env(monkeypatch)

    class _Engine:
        def connect(self):
            raise SQLAlchemyError("fail")

    monkeypatch.setattr(mysql_connector, "create_engine", lambda *_args, **_kwargs: _Engine())

    connector = MySQLConnector()

    with pytest.raises(DatabaseInitializationException):
        connector.create_db_if_not_exists()
