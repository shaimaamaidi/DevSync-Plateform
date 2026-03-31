"""
Unit tests for TokenCleanupScheduler.
"""

from unittest.mock import patch
from backend.src.infrastructure.scheduler.token_cleanup_scheduler import TokenCleanupScheduler


def test_scheduler_starts_and_stops():
    """
    Test that the scheduler starts and stops, calling the correct methods on BackgroundScheduler.
    """
    from unittest.mock import MagicMock
    with patch("backend.src.infrastructure.scheduler.token_cleanup_scheduler.BackgroundScheduler") as MockScheduler:
        instance = MockScheduler.return_value
        mock_db = MagicMock()
        scheduler = TokenCleanupScheduler(mock_db)
        scheduler.start()
        instance.start.assert_called_once()
        scheduler.stop()
        instance.shutdown.assert_called_once()
