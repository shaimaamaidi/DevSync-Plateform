"""
Unit tests for request id utilities used by logging.
"""

from backend.src.infrastructure.logging.request_id import (
    set_request_id,
    get_request_id,
    clear_request_id,
    RequestIdFilter,
)
from types import SimpleNamespace


def test_set_get_clear_request_id_roundtrip() -> None:
    """Setting and clearing request id should be reflected by get_request_id()."""
    set_request_id("abc-123")
    assert get_request_id() == "abc-123"

    clear_request_id()
    assert get_request_id() == "-"


def test_request_id_filter_attaches_request_id_to_record() -> None:
    """RequestIdFilter should add `request_id` attribute to log records."""
    set_request_id("req-42")

    record = SimpleNamespace()
    filter_instance = RequestIdFilter()

    result = filter_instance.filter(record)

    assert result is True
    assert getattr(record, "request_id") == "req-42"

    clear_request_id()
