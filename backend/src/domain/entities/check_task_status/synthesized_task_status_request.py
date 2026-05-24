"""
Domain DTO for task status synthesis requests.

This module defines the TaskStatusSynthesisRequest DTO used to represent
the input required to synthesize the status of a ClickUp task.
It encapsulates the target task and optional repository information
used to enrich the analysis (e.g., GitHub repository URL).

Main classes:
    SynthesizedTaskStatusRequest
"""

from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


class SynthesizedTaskStatusRequest(BaseModel, ABC):
    """
    Representation of a task status synthesis request.

    This DTO contains the necessary information to analyze and
    synthesize the current status of a ClickUp task, potentially
    using external repository context (e.g., GitHub).

    Attributes:
        repo_url: Optional URL of the source code repository related
            to the task. Used to enrich status analysis with commits
            and deployments context.
        task: ClickUp task to be analyzed and synthesized.
    """

    repo_url: Optional[str] = Field(
        default=None,
        description=(
            "Optional URL of the source code repository related to the task. "
            "Used to enrich status analysis with commits and deployments context."
        ),
    )
    task: ClickUpTask = Field(..., description="ClickUp task to be analyzed and synthesized.")