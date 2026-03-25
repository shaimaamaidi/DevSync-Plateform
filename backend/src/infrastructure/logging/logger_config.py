"""Logger configuration utilities for the application."""
import logging

from backend.src.infrastructure.logging.request_id import RequestIdFilter


def setup_logger() -> None:
    """Configure global logging settings for the application."""
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s [request_id=%(request_id)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    handler.addFilter(RequestIdFilter())

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    logging.captureWarnings(True)

    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.handlers = []
    sqlalchemy_logger.propagate = True