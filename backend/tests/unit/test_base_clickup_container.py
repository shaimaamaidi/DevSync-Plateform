"""
Unit tests for BaseClickUpContainer.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di import base_clickup_container
from backend.src.infrastructure.di.base_clickup_container import BaseClickUpContainer


def test_base_clickup_container_initializes_client_reader_and_writer(monkeypatch) -> None:
    """
    Test that the ClickUp container wires the HTTP client, reader, and writer.
    """
    http_client = MagicMock(name="http_client")
    clickup_reader = MagicMock(name="clickup_reader")
    clickup_writer = MagicMock(name="clickup_writer")

    monkeypatch.setattr(base_clickup_container, "ClickUpHttpClient", lambda: http_client)
    monkeypatch.setattr(base_clickup_container, "ClickUpReader", lambda client: clickup_reader if client is http_client else None)
    monkeypatch.setattr(base_clickup_container, "ClickUpTaskWriter", lambda client: clickup_writer if client is http_client else None)

    container = BaseClickUpContainer()

    assert container.http_client is http_client
    assert container.clickup_reader is clickup_reader
    assert container.clickup_writer is clickup_writer


def test_base_clickup_container_wraps_initialization_failure(monkeypatch) -> None:
    """
    Test that the ClickUp container raises an application error when initialization fails.
    """
    monkeypatch.setattr(base_clickup_container, "ClickUpHttpClient", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(AppException):
        BaseClickUpContainer()