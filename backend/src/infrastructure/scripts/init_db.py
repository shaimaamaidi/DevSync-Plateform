"""Database initialization script."""

import logging

from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.persistence.base import Base

from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel
from backend.src.infrastructure.persistence.models.member_repo_association import member_repo_association

from backend.src.domain.exceptions.app_exception import AppException


logger = logging.getLogger(__name__)


def init_db():
    """Create database and tables if they do not exist."""
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
        logger.error(
            "Application error during database initialization [%s]: %s.",
            e.code,
            e.message,
            exc_info=e,
        )
        raise

    except Exception as e:
        logger.error(
            "Application error during database initialization [%s]: %s.",
            e.code,
            e.message,
            exc_info=e,
        )
        raise

if __name__ == "__main__":
    init_db()