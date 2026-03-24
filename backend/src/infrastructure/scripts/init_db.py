from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.persistence.base import Base

from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel

from backend.src.domain.exceptions.app_exception import AppException


def init_db():
    print("🚀 Initializing database...")

    try:
        db = MySQLConnector()

        # Create DB if not exists
        db.create_db_if_not_exists()

        # Connect
        engine, Session = db.connect()

        # Create tables
        Base.metadata.create_all(engine)

        print("✅ Database and tables initialized successfully.")

    except AppException as e:
        print(f"❌ Application error: {e.message}")

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    init_db()