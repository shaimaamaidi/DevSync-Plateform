"""
Shared utility for ClickUp task context fetching.

This module provides a shared async utility function for retrieving
ClickUp task time context in parallel across multiple use cases.

Functions:
    fetch_task_context: Fetch time context for a single ClickUp task.
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
        Tuple of the original task and its time context dictionary.
    """
    task_context = await asyncio.to_thread(
        clickup_reader.get_task_time_context, task.id
    )
    return task, task_context