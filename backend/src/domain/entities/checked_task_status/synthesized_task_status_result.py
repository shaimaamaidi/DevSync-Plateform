"""
Domain DTO for task status synthesis results.

This module defines the TaskStatusSynthesisResult DTO used to represent
the synthesized status of a task based on analyzed information or evidence.
It encapsulates completion state, confidence level, generated summary,
and supporting evidence related to the task evaluation.

Main classes:
    SynthesizedTaskStatusResult
"""

from pydantic import BaseModel


class SynthesizedTaskStatusResult(BaseModel):
    """
    Representation of a synthesized task status result.

    This DTO contains the synthesized status information of a task,
    including whether the task is considered completed, the confidence
    level of the analysis, a summary describing the task state,
    and supporting evidence used during the evaluation.

    Attributes:
        is_completed: Indicates whether the task is considered completed.
        confidence: Confidence level of the synthesis result
            ("high", "medium", or "low").
        summary: Synthesized summary describing the task status.
        evidence: List of evidence entries supporting the synthesis result.
    """
    is_completed: bool
    confidence: str  # "high" | "medium" | "low"
    summary: str
    evidence: list[str]