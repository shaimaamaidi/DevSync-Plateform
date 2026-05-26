"""
Unit tests for logger configuration.
"""

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.src.infrastructure.logging.logger_config import _LoggerNameFilter, setup_logger
from backend.src.infrastructure.logging.request_id import RequestIdFilter


def test_logger_name_filter_normalizes_uvicorn_error() -> None:
    """
    Test that the logger name filter normalizes uvicorn.error records.
    """
    filter_instance = _LoggerNameFilter()
    record = SimpleNamespace(name="uvicorn.error")

    result = filter_instance.filter(record)

    assert result is True
    assert record.name == "uvicorn"


def test_setup_logger_configures_root_and_library_loggers(monkeypatch) -> None:
    """
    Test that setup_logger resets the root logger and adjusts common library loggers.
    """
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    named_loggers = {
        "uvicorn": MagicMock(handlers=["existing"], propagate=False),
        "uvicorn.error": MagicMock(handlers=["existing"], propagate=False),
        "uvicorn.access": MagicMock(handlers=["existing"], propagate=False),
        "sqlalchemy.engine": MagicMock(handlers=["existing"], propagate=False, level=logging.INFO),
        "sqlalchemy.engine.Engine": MagicMock(handlers=["existing"], propagate=False, level=logging.INFO),
    }
    real_get_logger = logging.getLogger

    def fake_get_logger(name=None):
        if name is None:
            return root_logger
        return named_loggers.get(name, real_get_logger(name))

    monkeypatch.setattr(logging, "getLogger", fake_get_logger)

    try:
        setup_logger()

        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1

        handler = root_logger.handlers[0]
        assert handler.level == logging.INFO
        assert handler.formatter is not None
        assert len(handler.filters) == 2
        assert any(isinstance(filter_instance, RequestIdFilter) for filter_instance in handler.filters)
        assert any(isinstance(filter_instance, _LoggerNameFilter) for filter_instance in handler.filters)

        assert named_loggers["uvicorn"].handlers == []
        assert named_loggers["uvicorn"].propagate is True
        assert named_loggers["uvicorn.error"].handlers == []
        assert named_loggers["uvicorn.error"].propagate is True
        assert named_loggers["uvicorn.access"].handlers == []
        assert named_loggers["uvicorn.access"].propagate is True
        assert named_loggers["sqlalchemy.engine"].handlers == []
        named_loggers["sqlalchemy.engine"].setLevel.assert_called_once_with(logging.WARNING)
        assert named_loggers["sqlalchemy.engine"].propagate is True
        assert named_loggers["sqlalchemy.engine.Engine"].handlers == []
        named_loggers["sqlalchemy.engine.Engine"].setLevel.assert_called_once_with(logging.WARNING)
        assert named_loggers["sqlalchemy.engine.Engine"].propagate is True
    finally:
        root_logger.handlers[:] = original_handlers
        root_logger.setLevel(original_level)
