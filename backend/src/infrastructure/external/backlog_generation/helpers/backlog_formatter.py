"""
Backlog formatter utility.

This module provides a helper function to convert a BacklogStructure domain entity
into a structured human-readable string format.

The formatted output is used as LLM context in backlog generation workflows,
including generation, cleaning, prioritization, and validation steps.

Main function:
    format_backlog: Transforms a BacklogStructure into a formatted string representation.
"""

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog


def format_backlog(backlog: BacklogStructure, include_task_desc: bool = True) -> str:
    """
    Convert a BacklogStructure into a human-readable string format.

    This function iterates through the backlog hierarchy (epics → user stories → tasks)
    and formats it into a structured text representation. It is primarily used to
    provide context to LLM agents during backlog generation workflows.

    Args:
        backlog (BacklogStructure): The backlog structure containing epics, user stories,
            and tasks to format.
        include_task_desc (bool, optional): Whether to include task description in.

    Returns:
        str: A formatted string representation of the entire backlog, including epics,
            user stories, and their associated tasks.
    """
    result = []

    for epic_block in backlog.epics:
        epic = epic_block.epic
        result.append(f"EPIC: {epic.title} — {epic.description}")

        for us_block in epic_block.user_stories:
            us = us_block.user_story
            result.append(f"  STORY: {us.title} — {us.description}")

            for task in us_block.tasks:
                if include_task_desc:
                    result.append(f"    TASK: {task.title}: {task.description}")
                else:
                    result.append(f"    TASK: {task.title}")

        result.append("")

    return "\n".join(result)

def format_epic(epic: EpicBacklog) -> str:
    """
    Convert a EpicBacklog into a human-readable string format.

    This function iterates through the epic hierarchy (epic → user stories → tasks)
    and formats it into a structured text representation. It is primarily used to
    provide context to LLM agents during backlog generation workflows.

    Args:
        epic (EpicBacklog): The epic structure containing user stories and tasks to format.

    Returns:
        str: A formatted string representation of the entire epic, including user stories,
            and their associated tasks.
    """
    result = [f"EPIC: {epic.epic.title}", f"Description: {epic.epic.description}\n"]

    for us_block in epic.user_stories:
        us = us_block.user_story
        result.append(f"  USER STORY: {us.title}")
        result.append(f"  Description: {us.description}")
        result.append("  TASKS:")

        for task in us_block.tasks:
            result.append(f"    - {task.title}: {task.description}")

        result.append("")


    return "\n".join(result)