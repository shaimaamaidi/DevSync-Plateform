"""
ClickUp assignee resolution exception.

This module defines the AssigneeEmailNotInClickUpException, raised when one or more
emails resolved from assignee names cannot be matched to ClickUp workspace members.
"""

from backend.src.domain.exceptions.base.app_exception import AppException


class AssigneeEmailNotInClickUpException(AppException):
    """
    Exception raised when assignee emails are not found in ClickUp workspace.

    This exception is used during task synchronization when the system attempts
    to assign users to ClickUp tasks, but one or more resolved emails do not match
    any existing ClickUp workspace members.

    Attributes:
        unresolved_emails (list[str]): List of emails that could not be matched.
        message (str): Human-readable error message describing the failure.
        code (str): Internal error code identifying the failure type.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, unresolved_emails: list[str]):
        """
        Initialize the ClickUp assignee resolution exception.

        Args:
            unresolved_emails (list[str]): Emails that could not be matched to ClickUp members.
        """
        self.unresolved_emails = unresolved_emails
        super().__init__(
            message=f"Assignee email(s) not found in ClickUp workspace: {unresolved_emails}",
            code="ASSIGNEE_EMAIL_NOT_IN_CLICKUP",
            http_status=422,
        )