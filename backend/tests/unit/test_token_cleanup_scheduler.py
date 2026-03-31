"""Unit tests for TokenCleanupScheduler."""

from unittest.mock import MagicMock, patch
import pytest
from backend.src.infrastructure.scheduler.token_cleanup_scheduler import TokenCleanupScheduler


def test_scheduler_starts_and_stops():
    with patch("backend.src.infrastructure.scheduler.token_cleanup_scheduler.BackgroundScheduler") as MockScheduler:
        scheduler = TokenCleanupScheduler()
        scheduler.start()
        MockScheduler.return_value.start.assert_called_once()
        scheduler.shutdown()
        MockScheduler.return_value.shutdown.assert_called_once()
