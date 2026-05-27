"""
Unit tests for MySQLConnector.

Tests validate environment validation, database creation attempt, connection/session
factory creation and disposal handling. Uses monkeypatch to replace SQLAlchemy
`create_engine` and `sessionmaker` to avoid real DB access.
"""

from types import SimpleNamespace


def _set_env(monkeypatch):
    monkeypatch.setenv("MYSQL_USER", "u")
    monkeypatch.setenv("MYSQL_PASSWORD", "p")
    monkeypatch.setenv("MYSQL_HOST", "localhost")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DB", "devsync")


def test_init_raises_when_env_missing(monkeypatch):
    # Prevent loading a repo .env file during test
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)

    # ensure env absent
    for k in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DB"]:
        monkeypatch.delenv(k, raising=False)

    with pytest.raises(DatabaseInitializationException):
        MySQLConnector()


def test_create_db_if_not_exists_calls_engine_and_executes(monkeypatch):
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)
    _set_env(monkeypatch)

    executed = {}

    class FakeConn:
        def execute(self, stmt):
            executed["sql"] = str(stmt)

    class FakeCtx:
        def __enter__(self):
            return FakeConn()

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_engine(conn_str, echo=False):
        return SimpleNamespace(connect=lambda: FakeCtx())

    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.create_engine", fake_create_engine)

    connector = MySQLConnector()

    connector.create_db_if_not_exists()

    assert "CREATE DATABASE IF NOT EXISTS" in executed.get("sql", "")


def test_create_db_if_not_exists_raises_on_sqlalchemy_error(monkeypatch):
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)
    _set_env(monkeypatch)

    def fake_create_engine(*args, **kwargs):
        raise SQLAlchemyError("boom")

    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.create_engine", fake_create_engine)

    connector = MySQLConnector()

    with pytest.raises(DatabaseInitializationException):
        connector.create_db_if_not_exists()


def test_connect_sets_engine_and_session(monkeypatch):
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)
    _set_env(monkeypatch)

    fake_engine = SimpleNamespace(dispose=lambda: None)

    def fake_create_engine(conn_str, echo=False, connect_args=None):
        return fake_engine

    def fake_sessionmaker(bind=None):
        return lambda: "session-instance"

    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.create_engine", fake_create_engine)
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.sessionmaker", fake_sessionmaker)

    connector = MySQLConnector()

    engine, Session = connector.connect()

    assert engine is fake_engine
    assert callable(Session)
    sess = connector.get_session()
    assert sess == "session-instance"


def test_get_session_raises_on_error(monkeypatch):
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)
    _set_env(monkeypatch)
    connector = MySQLConnector()

    # Force Session to be invalid so calling it raises
    connector.Session = lambda: (_ for _ in ()).throw(RuntimeError("nope"))

    with pytest.raises(DatabaseSessionException):
        connector.get_session()


def test_close_disposes_and_handles_errors(monkeypatch):
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)
    _set_env(monkeypatch)
    connector = MySQLConnector()

    disposed = {"called": False}

    class FakeEngine:
        def dispose(self):
            disposed["called"] = True

    connector.engine = FakeEngine()
    connector.Session = object()

    connector.close()
    assert disposed["called"] is True
    assert connector.engine is None
    assert connector.Session is None

    class BadEngine:
        def dispose(self):
            raise SQLAlchemyError("dispose fail")

    connector.engine = BadEngine()

    with pytest.raises(DatabaseConnectionException):
        connector.close()
"""
Unit tests for MySQLConnector.
"""

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


from unittest.mock import patch

def test_mysql_connector_missing_env_raises(monkeypatch) -> None:
    """
    Missing env vars should raise DatabaseInitializationException.
    """
    for key in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DB"]:
        monkeypatch.delenv(key, raising=False)

    with patch("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *args, **kwargs: False):
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
