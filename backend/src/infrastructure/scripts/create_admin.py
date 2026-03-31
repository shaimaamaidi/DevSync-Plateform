"""
Script to create a default admin member.

This script initializes the application container and creates
an admin user if it does not already exist.
"""

import logging

from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.di.container import Container
from backend.src.domain.entities.member import MemberCreateDTO


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

        logger.info("Checking if admin member already exists (mail=admin@gmail.com).")

        existing = member_service.get_member_by_mail("admin@gmail.com")

        if existing:
            logger.info("Admin member already exists (id=%s).", existing.id)
            return

        logger.info("Creating admin member.")

        member = MemberCreateDTO(
            username="admin",
            mail="admin@gmail.com",
            password="admin",
        )

        created = member_service.create_member(member)

        logger.info("Admin member created successfully (id=%s).", created.id)


if __name__ == "__main__":
    create_admin()