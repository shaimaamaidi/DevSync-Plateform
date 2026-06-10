"""
Token Cleanup Scheduler module.

This module provides the TokenCleanupScheduler class, which schedules and manages periodic cleanup of expired refresh tokens from the database using APScheduler. It loads configuration from environment variables and integrates with the MySQLConnector and SqlAlchemyRefreshTokenRepository.

Classes:
    TokenCleanupScheduler: Schedules and executes periodic cleanup jobs for expired refresh tokens.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.persistence.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository


logger = logging.getLogger(__name__)


class TokenCleanupScheduler:
    """
    Schedules and manages periodic cleanup of expired refresh tokens.

    This class uses APScheduler to periodically delete expired refresh tokens from the database. It loads configuration from environment variables and integrates with MySQLConnector and SqlAlchemyRefreshTokenRepository.

    Attributes:
        _db (MySQLConnector): The database connector instance.
        _interval_hours (int): Interval in hours between cleanup jobs.
        _scheduler (BackgroundScheduler): The APScheduler background scheduler instance.
    """

    def __init__(self, db: MySQLConnector):
        """
        Initialize the TokenCleanupScheduler.

        Args:
            db (MySQLConnector): The database connector instance.
        """
        self._db = db

        self._interval_hours = settings.TOKEN_CLEANUP_INTERVAL_HOURS

        self._scheduler = BackgroundScheduler()

    def _cleanup(self) -> None:
        """
        Delete expired refresh tokens from the database.

        This method is called by the scheduler to remove expired refresh tokens.
        """
        logger.info("Starting expired refresh token cleanup.")

        session = self._db.get_session()
        try:
            repo = SqlAlchemyRefreshTokenRepository(session)
            deleted = repo.delete_expired()

            logger.info("Cleaning up done — %d tokens deleted.", deleted)

        except Exception as e:
            logger.exception("Cleaning up failed: %s.", str(e))

        finally:
            session.close()

    def start(self) -> None:
        """
        Start the token cleanup scheduler.

        Schedules the periodic cleanup job and starts the background scheduler.

        Raises:
            Exception: If the scheduler fails to start (logged, not propagated).
        """
        self._scheduler.add_job(
            self._cleanup,
            trigger=IntervalTrigger(hours=self._interval_hours),
            id="refresh_token_cleanup",
            replace_existing=True,
        )
        self._scheduler.start()

        logger.info(
            "Token cleanup scheduler started (every %dh).",
            self._interval_hours
        )

    def stop(self) -> None:
        """
        Stop the token cleanup scheduler.

        Shuts down the background scheduler and stops all scheduled jobs.

        Raises:
            Exception: If the scheduler fails to shut down (logged, not propagated).
        """
        self._scheduler.shutdown()

        logger.info("Token cleanup scheduler stopped.")