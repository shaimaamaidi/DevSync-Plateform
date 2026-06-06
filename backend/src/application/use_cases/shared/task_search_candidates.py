"""
ClickUp task candidate filtering utilities for semantic search.

This module provides asynchronous helper functions to enrich ClickUp tasks
with contextual metadata and filter them into eligible candidates for
search and downstream AI/LLM processing.

It is primarily used to:
- Retrieve task context (creation and update timestamps)
- Filter out recently created tasks that are not suitable for search
- Rank remaining tasks by recency of updates
- Prepare a refined set of task candidates for semantic matching

Main responsibilities:
- Async enrichment of ClickUp tasks with metadata
- Temporal filtering based on creation date thresholds
- Prioritization based on update recency

Functions:
    filter_search_candidates: Enrich, filter, and rank ClickUp tasks
        into eligible candidates for semantic search operations.
"""

import asyncio
from datetime import timedelta, datetime
from typing import List

from backend.src.application.use_cases.shared.clickup_task_context import fetch_task_context
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


async def filter_search_candidates(
    clickup_reader:IClickUpReader,
    tasks: List[ClickUpTask]
) ->List[ClickUpTask]:
    """
    Filter and prioritize task candidates for search operations.

    This function enriches tasks with their contextual metadata,
    removes tasks that are too recent to be considered search
    candidates, and orders the remaining tasks by their most
    recent update date.

    Eligibility criteria:
    - The task must have a creation date.
    - The task must have been created at least 30 days ago.

    Sorting criteria:
    - Eligible tasks are sorted by their update date in descending
      order, with the most recently updated tasks appearing first.

    Args:
        clickup_reader: ClickUp reader port used to retrieve task
            contextual information.
        tasks: List of ClickUp tasks to evaluate.

    Returns:
        List of eligible tasks sorted by most recent update date.
        Returns an empty list if no eligible tasks are found.
    """
    tasks_with_context = await asyncio.gather(*[fetch_task_context(task, clickup_reader) for task in tasks])

    cutoff = datetime.now() - timedelta(days=30)

    eligible = [
        (task, ctx)
        for task, ctx in tasks_with_context
        if ctx.get("date_created") and ctx["date_created"] <= cutoff
    ]

    if not eligible:
        return []

    eligible.sort(
        key=lambda pair: pair[1].get("date_updated") or datetime.min,
        reverse=True
    )

    eligible_tasks = [task for task, _ in eligible]
    return eligible_tasks
