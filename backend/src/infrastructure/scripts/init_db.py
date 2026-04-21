"""
Database initialization script.

This script initializes the database and creates all required tables if they do not exist, using SQLAlchemy models and the MySQLConnector utility.

Functions:
    init_db: Initializes the database and creates tables.
"""

import logging

from backend.src.infrastructure.logging.logger_config import setup_logger
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.persistence.base import Base

from backend.src.domain.exceptions.base.app_exception import AppException


setup_logger()
logger = logging.getLogger(__name__)


def init_db():
    """
    Create database and tables if they do not exist.

    Initializes the MySQL database and creates all tables defined in the SQLAlchemy metadata.

    Raises:
        AppException: If a domain-specific application error occurs during initialization.
        Exception: For any other unexpected errors during initialization.
    """
    logger.info("Starting database initialization.")
    
    try:
        # Initialize connector
        logger.info("Initializing MySQL connector.")
        db = MySQLConnector()

        # Create DB if not exists
        logger.info("Ensuring database exists.")
        db.create_db_if_not_exists()

        # Connect
        logger.info("Connecting to database.")
        engine, Session = db.connect()

        # Create tables
        logger.info("Creating database tables from metadata.")
        Base.metadata.create_all(engine)

        logger.info("Database initialization completed successfully.")

    except AppException as e:
        logger.exception(
            "Application error during database initialization [%s].",
            str(e),
            exc_info=e
        )
        raise AppException("Database initialization failed") from e

    except Exception as e:
        logger.exception(
            "Application error during database initialization [%s].",
            str(e),
            exc_info=e
        )
        raise RuntimeError("Unexpected error during database initialization") from e

if __name__ == "__main__":
    init_db()