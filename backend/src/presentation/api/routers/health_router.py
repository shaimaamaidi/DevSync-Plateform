"""
Health Check API routes.

This module defines API endpoints for monitoring the service health status.

Routes:
    GET /: Retrieve the current health status of the service.
"""
import logging

from fastapi import APIRouter


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("", summary="Health check")
def health_check():
    """
    Retrieve the service health status.

    Returns:
        dict: A JSON payload indicating the service status.
    """
    logger.info("Health check endpoint called.")


    response = {"status": "ok"}

    logger.info("Health check successful: status=%s.", response["status"])

    return response