from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from backend.src.domain.exceptions.app_exception import AppException
from backend.src.domain.exceptions.database_connection_exception import DatabaseConnectionException
from backend.src.domain.exceptions.database_initialization_exception import DatabaseInitializationException
from backend.src.domain.exceptions.database_session_exception import DatabaseSessionException


class MySQLConnector:
    def __init__(self):
        load_dotenv()
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
            "MYSQL_DB": self.db,
        }.items() if not v]
        if missing:
            raise DatabaseInitializationException(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    def create_db_if_not_exists(self):
        try:
            engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}")
            with engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self.db}`"))
                print(f"Database `{self.db}` checked/created.")
        except SQLAlchemyError as e:
            raise DatabaseInitializationException() from e

    def connect(self):
        try:
            connection_string = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
            self.engine = create_engine(connection_string, echo=True)  # echo=True pour debug SQL
            self.Session = sessionmaker(bind=self.engine)
            return self.engine, self.Session
        except SQLAlchemyError as e:
            raise DatabaseConnectionException() from e

    def get_session(self):
        try:
            if not self.Session:
                self.connect()
            return self.Session()
        except AppException:
            raise
        except Exception as e:
            raise DatabaseSessionException() from e