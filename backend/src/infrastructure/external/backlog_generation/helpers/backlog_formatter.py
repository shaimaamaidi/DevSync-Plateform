"""
Backlog formatter utility.

This module provides a helper function to convert a BacklogStructure domain entity
into a structured human-readable string format.

The formatted output is used as LLM context in backlog generation workflows,
including generation, cleaning, prioritization, and validation steps.

Main function:
    format_backlog: Transforms a BacklogStructure into a formatted string representation.
"""

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure


def format_backlog(backlog: BacklogStructure) -> str:
    """
    Convert a BacklogStructure into a human-readable string format.

    This function iterates through the backlog hierarchy (epics → user stories → tasks)
    and formats it into a structured text representation. It is primarily used to
    provide context to LLM agents during backlog generation workflows.

    Args:
        backlog (BacklogStructure): The backlog structure containing epics, user stories,
            and tasks to format.

    Returns:
        str: A formatted string representation of the entire backlog, including epics,
            user stories, and their associated tasks.
    """
    result = []

    for epic_block in backlog.epics:
        epic = epic_block.epic
        result.append(f"EPIC: {epic.title}")
        result.append(f"Description: {epic.description}\n")

        for us_block in epic_block.user_stories:
            us = us_block.user_story
            result.append(f"  USER STORY: {us.title}")
            result.append(f"  Description: {us.description}")
            result.append("  TASKS:")

            for task in us_block.tasks:
                result.append(f"    - {task.title}: {task.description}")

            result.append("")

        result.append("-" * 50)

    return "\n".join(result)