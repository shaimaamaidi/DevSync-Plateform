"""
SQLAlchemy base metadata for persistence models.
"""

import logging

from sqlalchemy.orm import declarative_base


logger = logging.getLogger(__name__)


Base = declarative_base()

logger.info("SQLAlchemy Base metadata initialized.")

class BaseModel(Base):
    __abstract__ = True

    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }