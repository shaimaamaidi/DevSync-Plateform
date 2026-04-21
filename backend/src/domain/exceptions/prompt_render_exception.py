"""
Prompt render exception.

This module defines the PromptRenderException, raised when a prompt template
cannot be rendered correctly during the rendering process. It is triggered when
template rendering fails due to invalid variables, missing context, or internal
processing errors.
"""

from backend.src.domain.exceptions.app_exception import AppException


class PromptRenderException(AppException):
    """
    Exception raised when a prompt template rendering fails.

    This exception is used when the system is unable to render a prompt template
    due to issues such as invalid input variables, missing rendering context,
    malformed templates, or runtime Jinja2 rendering errors.

    Attributes:
        message (str): Human-readable error message describing the rendering failure.
        code (str): Internal error code identifying the rendering error.
        http_status (int): HTTP status code returned to the client.
    """

    def __init__(self, message: str = "Failed to render prompt template."):
        """
        Initialize a PromptRenderException.

        Args:
            message (str): Error message describing the rendering failure.
                This should include context such as prompt name, rendering step,
                or underlying cause of the failure.
        """
        super().__init__(
            message=message,
            code="PROMPT_RENDER_ERROR",
            http_status=500,
        )