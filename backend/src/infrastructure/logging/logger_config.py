"""Logging configuration for the API server."""

import logging

from backend.src.infrastructure.logging.request_id import RequestIdFilter


class _LoggerNameFilter(logging.Filter):
    """Normalize logger names for consistent output."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Adjust logger name values for display.

        Args:
            record: Log record instance.

        Returns:
            True to keep the record.
        """
        
        if record.name == "uvicorn.error":
            record.name = "uvicorn"
        return True


def setup_logger() -> None:
    """Configure the root logger and common libraries."""
    
    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s [request_id=%(request_id)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    handler.addFilter(RequestIdFilter())
    handler.addFilter(_LoggerNameFilter())

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    logging.captureWarnings(True)

    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.handlers = []
    sqlalchemy_logger.setLevel(logging.WARNING)
    sqlalchemy_logger.propagate = True

    sqlalchemy_engine_logger = logging.getLogger("sqlalchemy.engine.Engine")
    sqlalchemy_engine_logger.handlers = []
    sqlalchemy_engine_logger.setLevel(logging.WARNING)
    sqlalchemy_engine_logger.propagate = True