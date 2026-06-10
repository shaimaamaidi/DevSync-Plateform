"""
Delivery plan exception module.

This module defines the DeliveryPlanException, raised when an error occurs
during the delivery planning workflow, such as failed sprint generation,
invalid backlog input, or unexpected runtime issues while producing
the prioritized backlog and sprint plan.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class DeliveryPlanException(AppException):
    """
    Exception raised when a delivery planning process fails.

    This exception is used to indicate failures occurring during delivery
    plan generation, including invalid backlog input, sprint planning errors,
    or unexpected runtime issues while processing the confirmed backlog
    into a structured delivery plan.

    Attributes:
        message (str): Human-readable error message describing the failure.
        code (str): Internal error code identifying the delivery plan error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to generate delivery plan. Please try again."):
        """
        Initialize a delivery plan exception.

        Args:
            message (str): Error message describing the delivery plan failure.
        """
        super().__init__(
            message=message,
            code="DELIVERY_PLAN_ERROR",
            http_status=503,
        )