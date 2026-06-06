"""
ClickUp task helper utilities module.

This module provides utility functions for grouping, organizing, and extracting
metadata from ClickUp tasks. It supports both existing ClickUp tasks and
generated tasks, and provides helpers for debugging and analysis.

Functions:
    get_tasks_by_folder: Group existing ClickUp tasks by folder.
    get_generated_tasks_by_folder: Group generated tasks by folder.
    get_folders_statuses_and_priorities: Extract statuses and priorities per folder.
"""

import logging
from typing import List, Dict

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.generated_tasks.generated_task_from_backlog import GeneratedTaskFromBacklog
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary


logger = logging.getLogger(__name__)


def get_tasks_by_location(folders) -> Dict[str, List[ClickUpTask]]:
    """
    Group existing tasks by location label.

    Location label format:
    - "FolderName / ListName" for lists inside a folder
    - "ListName" for folderless lists (folder.id == lst.id)

    Args:
        folders: Iterable of Folder objects containing lists and tasks.

    Returns:
        Mapping of location label to a list of Task instances.
    """
    result: Dict[str, List[ClickUpTask]] = {}

    for folder in folders:
        for lst in folder.lists:
            label = lst.name if folder.id == lst.id else f"{folder.name} / {lst.name}"
            result.setdefault(label, []).extend(lst.tasks)

    logger.info(
        "Existing tasks grouped by location: %s",
        {label: len(tasks) for label, tasks in result.items()},
    )

    return result


def get_generated_tasks_from_summary_by_location(generated_tasks: List[GeneratedTaskFromSummary]) -> Dict[str, List[GeneratedTaskFromSummary]]:
    """
    Group generated tasks by location label.

    Args:
        generated_tasks: List of GeneratedTask instances.

    Returns:
        Mapping of location label to a list of GeneratedTask instances.
    """
    result: Dict[str, List[GeneratedTaskFromSummary]] = {}

    for task in generated_tasks:
        result.setdefault(task.location, []).append(task)

    logger.info(
        "Generated tasks grouped by location: %s",
        {label: len(tasks) for label, tasks in result.items()},
    )

    return result

def get_generated_tasks_from_backlog_by_location(generated_tasks: List[GeneratedTaskFromBacklog]) -> Dict[str, List[GeneratedTaskFromBacklog]]:
    """
    Group generated tasks by location label.

    Args:
        generated_tasks: List of GeneratedTaskFromBacklog instances.

    Returns:
        Mapping of location label to a list of GeneratedTask instances.
    """
    result: Dict[str, List[GeneratedTaskFromBacklog]] = {}

    for task in generated_tasks:
        result.setdefault(task.location, []).append(task)

    logger.info(
        "Generated tasks grouped by location: %s",
        {label: len(tasks) for label, tasks in result.items()},
    )

    return result

def get_folders_statuses_and_priorities(folders: List[FolderWithListsMetadata]) -> Dict[str, Dict[str, List[str]]]:
    """
    Collect statuses and priorities available per folder.

    Args:
        folders: Iterable of Folder objects containing lists and metadata.

    Returns:
        Mapping of location label to available statuses and priorities.
        - Folderless lists: labelled by list name only  → "Backlog"
        - Lists inside a folder: labelled as folder/list → "Dev / Backend"

        Example:
            {
                "Dev / Backend": {
                    "statuses": ["to do", "in progress", "done"],
                    "priorities": ["urgent", "high", "normal", "low"],
                },
                "Backlog": {
                    "statuses": ["open", "closed"],
                    "priorities": ["urgent", "high", "normal", "low"],
                },
            }
    """
    folders_info: Dict[str, Dict[str, set]] = {}

    for folder in folders:
        for lst in folder.lists:
            # Folderless: folder.id == lst.id (synthetic folder created per list)
            label = lst.name if folder.id == lst.id else f"{folder.name} / {lst.name}"

            if label not in folders_info:
                folders_info[label] = {"statuses": set(), "priorities": set()}

            for status in lst.statuses:
                folders_info[label]["statuses"].add(status)

            for priority in lst.priorities:
                folders_info[label]["priorities"].add(priority)

    result = {
        label: {
            "statuses": list(info["statuses"]),
            "priorities": list(info["priorities"]),
        }
        for label, info in folders_info.items()
    }

    logger.info(
        "Folders statuses and priorities extracted: %s",
        {name: {"statuses": data["statuses"], "priorities": data["priorities"]}
         for name, data in result.items()},
    )

    return result

def get_folders_priorities(folders: List[FolderWithListsMetadata]) -> Dict[str, Dict[str, List[str]]]:
    """
    Collect statuses and priorities available per folder.

    Args:
        folders: Iterable of Folder objects containing lists and metadata.

    Returns:
        Mapping of location label to available statuses and priorities.
        - Folderless lists: labelled by list name only  → "Backlog"
        - Lists inside a folder: labelled as folder/list → "Dev / Backend"

        Example:
            {
                "Dev / Backend": {
                    "priorities": ["urgent", "high", "normal", "low"],
                },
                "Backlog": {
                    "priorities": ["urgent", "high", "normal", "low"],
                },
            }
    """
    folders_info: Dict[str, Dict[str, set]] = {}

    for folder in folders:
        for lst in folder.lists:
            # Folderless: folder.id == lst.id (synthetic folder created per list)
            label = lst.name if folder.id == lst.id else f"{folder.name} / {lst.name}"

            if label not in folders_info:
                folders_info[label] = {"statuses": set(), "priorities": set()}

            for priority in lst.priorities:
                folders_info[label]["priorities"].add(priority)

    result = {
        label: {
            "priorities": list(info["priorities"]),
        }
        for label, info in folders_info.items()
    }

    logger.info(
        "Folders statuses and priorities extracted: %s",
        {name: {"priorities": data["priorities"]}
         for name, data in result.items()},
    )

    return result