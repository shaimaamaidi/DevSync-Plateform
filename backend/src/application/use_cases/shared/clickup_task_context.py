"""
ClickUp task context retrieval utilities.

This module provides asynchronous helper functions for retrieving
contextual metadata for ClickUp tasks in a non-blocking way.

It is mainly used to enrich tasks with time-based information
(such as creation and update dates) before downstream processing
like filtering, search, or AI-based matching.

Functions:
    fetch_task_context: Retrieve contextual metadata for a single
        ClickUp task using a non-blocking async wrapper around
        synchronous ClickUp API calls.
"""

import asyncio
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.ports.output.clickup.i_clickup_reader import IClickUpReader


async def fetch_task_context(
    task: ClickUpTask,
    clickup_reader: IClickUpReader,
) -> tuple[ClickUpTask, dict]:
    """
    Fetch the time context for a single ClickUp task in a thread executor.

    Wraps the synchronous get_task_time_context call using asyncio.to_thread
    to avoid blocking the event loop.

    Args:
        task: ClickUp task for which to retrieve the time context.
        clickup_reader: ClickUp reader port used to fetch task time context.

    Returns:
        Tuple containing:
        - The original ClickUp task
        - A dictionary with contextual metadata (e.g., creation/update dates)
    """
    task_context = await asyncio.to_thread(
        clickup_reader.get_task_time_context, task.id
    )
    return task, task_context