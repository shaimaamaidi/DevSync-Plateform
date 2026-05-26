"""
Domain DTO for task search requests.

This module defines the TaskSearchRequest DTO used to represent
a task search request initiated by a user.
It encapsulates the target ClickUp space identifier and
the natural language question used for searching tasks.

Main classes:
    TaskSearchRequest
"""

from pydantic import Field, BaseModel


class TaskSearchRequest(BaseModel):
    """
    Representation of a task search request.

    This DTO contains the information required to perform
    a task search operation within a ClickUp space using
    a natural language query.

    Attributes:
        space_id: Identifier of the ClickUp space where tasks
            should be searched.
        question: User natural language query describing
            the search intent.
    """
    space_id: str = Field(..., min_length=1, description="Identifier of the ClickUp space where tasks should be searched.")
    question: str = Field(..., min_length=1, description="User natural language query describing the search intent.")