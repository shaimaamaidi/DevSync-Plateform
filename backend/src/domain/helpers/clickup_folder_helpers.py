"""
ClickUp task helper utilities module.

This module provides utility functions for grouping, organizing, and extracting
metadata from ClickUp tasks. It supports both existing ClickUp tasks and
generated tasks, and provides helpers for debugging and analysis.

Functions:
    get_tasks_by_folder: Group existing ClickUp tasks by folder.
    get_generated_tasks_by_folder: Group generated tasks by folder.
    print_tasks_by_folder: Debug print existing tasks by folder.
    print_generated_tasks_by_folder: Debug print generated tasks by folder.
    get_folders_statuses_and_priorities: Extract statuses and priorities per folder.
"""

import logging
from typing import List, Dict

from backend.src.domain.entities.clickup.list import ClickUpTask
from backend.src.domain.entities.generate_tasks_from_summary.generated_task import GeneratedTask


logger = logging.getLogger(__name__)


def get_tasks_by_folder(folders) -> Dict[str, List[ClickUpTask]]:
    """
    Group existing ClickUp tasks by folder name.

    This function traverses folders and their lists to aggregate all tasks
    under their respective folder.

    Args:
        folders: Iterable of Folder objects containing lists and tasks.

    Returns:
        Dict[str, List[ClickUpTask]]: Mapping of folder name to tasks.
    """
    result: Dict[str, List[ClickUpTask]] = {}

    for folder in folders:
        tasks: List[ClickUpTask] = []
        for lst in folder.lists:
            tasks.extend(lst.tasks)
        result[folder.name] = tasks

    logger.info(
        "Existing tasks grouped by folder: %s",
        {name: len(tasks) for name, tasks in result.items()},
    )

    return result


def get_generated_tasks_by_folder(generated_tasks: List[GeneratedTask]) -> Dict[str, List[GeneratedTask]]:
    """
    Group generated tasks by folder name.

    Args:
        generated_tasks (List[GeneratedTask]): List of generated tasks.

    Returns:
        Dict[str, List[GeneratedTask]]: Mapping of folder name to generated tasks.
    """
    result: Dict[str, List[GeneratedTask]] = {}

    for task in generated_tasks:
        folder = task.folder
        if folder not in result:
            result[folder] = []
        result[folder].append(task)

    logger.info(
        "Generated tasks grouped by folder: %s",
        {name: len(tasks) for name, tasks in result.items()},
    )

    return result

def print_tasks_by_folder(tasks_by_folder: Dict[str, List[ClickUpTask]]) -> None:
    """Print grouped tasks to stdout.

    Args:
        tasks_by_folder: Mapping of folder name to existing tasks.

    Returns:
        None.
    """
    for folder_name, tasks in tasks_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.name}")
                print(f"    Description: {task.description}")
        else:
            print("  (No tasks)")


def print_generated_tasks_by_folder(generated_by_folder: Dict[str, List[GeneratedTask]]) -> None:
    """Print grouped generated tasks to stdout.

    Args:
        generated_by_folder: Mapping of folder name to generated tasks.

    Returns:
        None.
    """
    for folder_name, tasks in generated_by_folder.items():
        print(f"Folder: {folder_name}")
        if tasks:
            for task in tasks:
                print(f"  - Name: {task.task_name}")
                print(f"    Description: {task.task_description}")
        else:
            print("  (No tasks)")

def get_folders_statuses_and_priorities(folders) -> Dict[str, Dict[str, List[str]]]:
    """
    Extract available statuses and priorities per folder.

    This function scans all lists inside folders and aggregates:
    - statuses
    - priorities

    Args:
        folders: Iterable of Folder objects containing lists and metadata.

    Returns:
        Dict[str, Dict[str, List[str]]]: Mapping of folder name to:
            - statuses: list of available statuses
            - priorities: list of available priorities
        Example:
            {
                "folder_name": {
                    "statuses": ["to do", "in progress", "done"],
                    "priorities": ["low", "medium", "high"],
                }
            }
    """
    folders_info: Dict[str, Dict[str, set]] = {}

    for folder in folders:

        if folder.name not in folders_info:
            folders_info[folder.name] = {"statuses": set(), "priorities": set()}

        for lst in folder.lists:
            # Add statuses defined on the list
            for status in lst.statuses:
                folders_info[folder.name]["statuses"].add(status)

            # Add priorities defined on the list
            for priority in lst.priorities:
                folders_info[folder.name]["priorities"].add(priority)

    result = {
        folder: {
            "statuses": list(info["statuses"]),
            "priorities": list(info["priorities"]),
        }
        for folder, info in folders_info.items()
    }

    logger.info(
        "Folders statuses and priorities extracted: %s",
        {name: {"statuses": data["statuses"], "priorities": data["priorities"]}
         for name, data in result.items()},
    )

    return result
