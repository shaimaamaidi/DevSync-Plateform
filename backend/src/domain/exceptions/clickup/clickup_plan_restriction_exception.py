"""
ClickUp plan restriction exception.

This module defines the ClickUpPlanRestrictionException, raised when a
ClickUp API operation is unavailable due to the workspace's current plan.
"""

from backend.src.domain.exceptions.clickup.clickup_write_exception import ClickUpWriteException


class ClickUpPlanRestrictionException(ClickUpWriteException):
    """
    Exception raised when a ClickUp API operation requires a higher plan.

    This exception is raised when the ClickUp API rejects a request because
    the workspace's current plan does not include the requested feature
    (e.g., inviting members via API requires an Enterprise plan).

    Attributes:
        message: Human-readable error message.
        code: Stable internal error code identifying the error type.
        http_status: HTTP status code (403 Forbidden).
    """

    def __init__(
        self,
        message: str = "This operation is not available on your current ClickUp plan.",
    ):
        """
        Initialize a ClickUp plan restriction exception.

        Args:
            message (str): Human-readable error message describing the restriction.
        """
        super().__init__(
            message=message,
            http_status=403,
        )
        self.code = "CLICKUP_PLAN_RESTRICTION"