"""
ClickUp assignee name resolution exception.

This module defines the AssigneeNameNotFoundException, raised when one or more
assignee names cannot be resolved using the internal name-to-email mapping.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class AssigneeNameNotFoundException(AppException):
    """
    Exception raised when assignee names cannot be resolved to emails.

    This exception is used during task synchronization when one or more assignee
    names cannot be found in the internal name-to-email mapping required to
    assign ClickUp workspace members.

    Attributes:
        unresolved_names (list[str]): List of names that could not be matched.
        message (str): Human-readable error message describing the failure.
        code (str): Internal error code identifying the failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, unresolved_names: list[str]):
        """
        Initialize the ClickUp assignee name resolution exception.

        Args:
            unresolved_names (list[str]): Names that could not be matched to email addresses.
        """
        self.unresolved_names = unresolved_names
        super().__init__(
            message=f"Assignee name(s) not found in name mapping: {unresolved_names}",
            code="ASSIGNEE_NAME_NOT_FOUND",
            http_status=422,
        )