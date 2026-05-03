"""
Domain DTO for ClickUp task saving response.

This module defines the response structure returned after persisting verified tasks
into ClickUp. It provides a summary of the execution result, including confirmation
status and number of processed tasks.

Main class:
    SaveTasksResponse
"""

from pydantic import BaseModel, Field


class SaveTasksResponse(BaseModel):
    """
    Representation of the result of saving tasks into ClickUp.

    This DTO confirms the successful execution of the task persistence workflow.
    It provides a human-readable message along with execution metadata.

    Attributes:
        message: Confirmation message describing the outcome of the operation.
        total_tasks: Total number of tasks processed during the save operation.
    """

    message: str = Field(
        ...,
        description="Human-readable confirmation message of the save operation."
    )

    total_tasks: int = Field(
        ...,
        description="Number of tasks successfully processed (created or updated)."
    )