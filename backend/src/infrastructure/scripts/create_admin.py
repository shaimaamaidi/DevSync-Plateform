"""
Script to create a default admin member.

This script initializes the application container and creates
an admin user if it does not already exist.
"""

import logging

from backend.src.infrastructure.logging.logger_config import setup_logger
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.di.persistence_container import Container
from backend.src.domain.entities.member import MemberCreateDTO


setup_logger()
logger = logging.getLogger(__name__)


def create_admin():
    """
    Create a default admin member if not exists.

    Returns:
        None: This function creates the admin user in the database.
    """
    db = MySQLConnector()
    engine, Session = db.connect()

    with Session() as session:
        container = Container(session)
        member_service = container.member_service

        logger.info("Creating admin member.")

        member = MemberCreateDTO(
            username="admin",
            arabic_name="شيماء",
            mail="admin@gmail.com",
            password="admin",
        )

        created = member_service.add_member(member)

        logger.info("Admin member created successfully (id=%s).", created.id)


if __name__ == "__main__":
    create_admin()