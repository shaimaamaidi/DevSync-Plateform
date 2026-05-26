"""
Domain DTO for weekly summary narrative.

This module defines the WeeklySummaryNarrative DTO used to represent
a natural language summary generated from weekly project activity.

It is used specifically to encapsulate LLM-generated summaries of:
- Weekly GitHub commits activity
- Weekly GitHub deployments activity

This DTO is shared by summarization services in order to return a unified
human-readable narrative describing the overall weekly development progress.

Main usage:
    - Weekly commits summarization
    - Weekly deployments summarization

Main classes:
    WeeklySummaryNarrative
"""

from pydantic import BaseModel


class WeeklySummaryNarrative(BaseModel):
    """
    Representation of a generated weekly project summary narrative.

    This model is used as the output of LLM-based summarization services
    that analyze weekly GitHub activity, including commits and deployments,
    and produce a single coherent narrative.

    Attributes:
        summary: Human-readable textual summary describing weekly
            commits and deployments activity, highlighting progress,
            releases, and development trends.
    """
    summary: str