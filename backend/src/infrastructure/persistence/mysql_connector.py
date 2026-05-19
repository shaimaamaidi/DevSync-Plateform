"""
MySQL database connector and session factory.

This module provides the MySQLConnector class for managing SQLAlchemy engine and session creation, loading configuration from environment variables, and ensuring the target database exists.
"""

import logging
from pathlib import Path
from typing import Tuple

from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.domain.exceptions.database.database_connection_exception import DatabaseConnectionException
from backend.src.domain.exceptions.database.database_initialization_exception import DatabaseInitializationException
from backend.src.domain.exceptions.database.database_session_exception import DatabaseSessionException


logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[3]
_DOTENV_PATH = _BACKEND_DIR / ".env"


class MySQLConnector:
    """
    Create and manage SQLAlchemy engine and sessions.

    This connector loads configuration from environment variables, ensures the database exists, and provides SQLAlchemy engine and session management.

    Attributes:
        user (str): MySQL username loaded from environment variables.
        password (str): MySQL password loaded from environment variables.
        host (str): MySQL host address loaded from environment variables.
        port (str): MySQL port loaded from environment variables.
        db (str): Target database name loaded from environment variables.
        engine (Engine | None): SQLAlchemy engine instance once connected.
        Session (sessionmaker[Session] | None): SQLAlchemy session factory once connected.
    """

    def __init__(self):
        """
        Initialize configuration from environment and validate it.

        Raises:
            DatabaseInitializationException: If required environment variables are missing.
        """
        logger.info("Initializing MySQL connector.")

        loaded = load_dotenv(_DOTENV_PATH, override=False)

        if not loaded:
            logger.warning(".env file not found at %s.", _DOTENV_PATH)

        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.host = os.getenv("MYSQL_HOST")
        self.port = os.getenv("MYSQL_PORT")
        self.db = os.getenv("MYSQL_DB")
        self.engine = None
        self.Session = None

        missing = [k for k, v in {
            "MYSQL_USER": self.user,
            "MYSQL_PASSWORD": self.password,
            "MYSQL_HOST": self.host,
            "MYSQL_PORT": self.port,
            "MYSQL_DB": self.db,
        }.items() if not v]

        if missing:
            logger.error(
                "Missing required environment variables for database: %s.",
                missing
            )
            raise DatabaseInitializationException(
                "The service is not properly configured. Please contact support."
            )

        logger.info(
            "MySQLConnector initialized (host=%s, port=%s, db=%s).",
            self.host,
            self.port,
            self.db
        )

    def create_db_if_not_exists(self):
        """
        Ensure the database exists before connecting.

        Raises:
            DatabaseInitializationException: If database creation fails.
        """
        logger.info(
            "Ensuring database exists (db=%s, host=%s).",
        
            self.db,
            self.host
        )

        try:
            engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}", echo=False)
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self.db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))

            logger.info("Database '%s' is ready.", self.db)

        except SQLAlchemyError as e:
            logger.exception(
                "Failed to create or verify database '%s': %s.",
                self.db,
                str(e)
            )
            raise DatabaseInitializationException() from e

    def connect(self) -> Tuple[Engine, sessionmaker]:
        """
        Create a SQLAlchemy engine and session factory.

        Returns:
             Tuple[Engine, sessionmaker]: Tuple of (engine, sessionmaker).

        Raises:
            DatabaseConnectionException: If engine or session factory creation fails.
        """
        logger.info(
            "Connecting to MySQL database (host=%s, port=%s, db=%s).",
            self.host,
            self.port,
            self.db
        )

        try:
            connection_string = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}?charset=utf8mb4"
            self.engine = create_engine(connection_string, echo=False, connect_args={"charset": "utf8mb4"})
            self.Session = sessionmaker(bind=self.engine)

            logger.info("Database connection established successfully.")

            return self.engine, self.Session

        except SQLAlchemyError as e:
            logger.exception(
                "Database connection failed (host=%s, db=%s): %s.",
                self.host,
                self.db,
                str(e)
            )
            raise DatabaseConnectionException() from e

    def get_session(self) -> Session:
        """
        Create a new SQLAlchemy session.

        Returns:
            Session: SQLAlchemy session instance.

        Raises:
            DatabaseSessionException: If session creation fails.
        """
        logger.info("Creating new database session.")

        try:
            if not self.Session:
                logger.warning("Session factory not initialized, connecting to database.")

                self.connect()

                logger.info("Database session established successfully.")

            return self.Session()

        except AppException:
            raise
        except Exception as e:
            logger.exception(
                "Failed to create database session: %s.",
                str(e)
            )
            raise DatabaseSessionException() from e

    def close(self) -> None:
        """
        Dispose the SQLAlchemy engine and release all pooled connections.

        Sends COM_QUIT to each connection in the pool so MySQL frees
        the slots immediately instead of waiting for wait_timeout.

        Raises:
            DatabaseConnectionException: If engine disposal fails.
        """
        logger.info("Closing MySQL connector (host=%s, db=%s).", self.host, self.db)

        if self.engine is None:
            logger.warning("Engine not initialized, nothing to close.")
            return

        try:
            self.engine.dispose()
            self.engine = None
            self.Session = None
            logger.info("MySQL engine disposed successfully.")
        except SQLAlchemyError as e:
            logger.exception("Failed to dispose MySQL engine.")
            raise DatabaseConnectionException() from e