"""
Domain helpers for resolving ClickUp assignees and task priorities.

This module defines utility functions used to map human-readable assignee names
and priority labels into ClickUp-compatible identifiers. It handles mapping
between assignee identifiers and ClickUp workspace members.
"""

import logging
from typing import List, Dict, Optional

from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask, ClickUpTaskWithEstimation
from backend.src.domain.exceptions.clickup.clickup_assignee_email_not_found_exception import \
    AssigneeEmailNotInClickUpException
from backend.src.domain.exceptions.clickup.clickup_assignee_name_not_found_exception import \
    AssigneeNameNotFoundException


logger = logging.getLogger(__name__)


def resolve_assignee_ids_from_mails(
        email_to_id: Dict[str, int],
        assignee_mails: List[str],
        ignore_mails: bool
) -> List[int]:
    """
    Resolve assignee mails to ClickUp member IDs.

    This function converts assignee mails into ClickUp user IDs using
    provided mapping dictionaries. If some assignees cannot be resolved,
    behavior depends on the `ignore_mails` flag.

    Args:
        email_to_id (Dict[str, int]): Mapping of email addresses to ClickUp member IDs.
        assignee_mails (List[str]): List of assignee mails to resolve.
        ignore_mails (bool):
            If True, unresolved assignees are ignored.
            If False, an exception is raised when resolution fails.

    Returns:
        List[int]: List of resolved ClickUp member IDs.

    Raises:
        AssigneeEmailNotInClickUpException: Raised when one or more mapped emails are not
            found in the ClickUp workspace and `ignore_mails=False`.
    """
    logger.info(
        "Starting assignee resolution (strict). input_count=%d.",
        len(assignee_mails),
    )

    resolved = []
    unresolved_emails = []

    for mail in assignee_mails:
        member_id = email_to_id.get(mail.lower())

        if not member_id:
            logger.warning(
                "mail '%s' not found in ClickUp workspace.",
                mail,
            )
            unresolved_emails.append(mail)

        else:
            resolved.append(member_id)

    if unresolved_emails and not ignore_mails:
        raise AssigneeEmailNotInClickUpException(unresolved_emails)

    logger.info(
        "Assignee resolution (strict): %d/%d resolved.",
        len(resolved),
        len([n for n in assignee_mails if n ]),
    )

    return resolved

def resolve_assignee_ids_strict(
        name_to_email: dict,
        email_to_id: Dict[str, int],
        assignee_names: List[str],
        ignore_names: bool,
        ignore_mails: bool
) -> List[int]:
    """
    Resolve assignee names to ClickUp member IDs.

    This function converts assignee names into ClickUp user IDs using
    provided mapping dictionaries. If some assignees cannot be resolved,
    behavior depends on the `ignore_mails` and `ignore_names` flag.

    Args:
        name_to_email (dict): Mapping of assignee names to email addresses.
        email_to_id (Dict[str, int]): Mapping of email addresses to ClickUp member IDs.
        assignee_names (List[str]): List of assignee names to resolve.
        ignore_names (bool):
            If True, names without an email mapping are ignored.
            If False, an exception is raised for unresolved names.
        ignore_mails (bool):
            If True, unresolved assignees are ignored.
            If False, an exception is raised when resolution fails.

    Returns:
        List[int]: List of resolved ClickUp member IDs.

    Raises:
        AssigneeNameNotFoundException: Raised when one or more assignee names cannot be
            mapped to emails and `ignore_names=False`.
        AssigneeEmailNotInClickUpException: Raised when one or more mapped emails are not
            found in the ClickUp workspace and `ignore_mails=False`.
    """
    logger.info(
        "Starting assignee resolution (strict). input_count=%d.",
        len(assignee_names),
    )

    resolved = []
    unresolved_emails = []
    unresolved_names = []

    for name in assignee_names:
        if not name or name == "غير محدد":
            logger.warning("Skipping invalid assignee name: '%s'.", name)
            continue

        mail = name_to_email.get(name.lower())

        if not mail:
            logger.warning("No email mapping found for assignee name: '%s'.", name)
            unresolved_names.append(name)
            continue

        member_id = email_to_id.get(mail.lower())

        if not member_id:
            logger.warning(
                "mail '%s' matched for '%s' but not found in ClickUp workspace.",
                mail,
                name,
            )
            unresolved_emails.append(mail)

        else:
            resolved.append(member_id)

    if unresolved_names and not ignore_names:
        raise AssigneeNameNotFoundException(unresolved_names)

    if unresolved_emails and not ignore_mails:
        raise AssigneeEmailNotInClickUpException(unresolved_emails)

    logger.info(
        "Assignee resolution (strict): %d/%d resolved.",
        len(resolved),
        len([n for n in assignee_names if n and n != "غير محدد"]),
    )

    return resolved


def priority_to_str(priority: str | None) -> str | None :
    """
    Convert a priority label to a string ranking.

    This function normalizes ClickUp priority labels into a string scale
    where lower values represent higher priority.

    Args:
        priority: Priority label (e.g., "urgent", "high", "normal", "low").

    Returns:
        str: string priority rank ("1" = highest, "4" = lowest).
    """
    mapping = {
        "urgent": "1",
        "high": "2",
        "normal": "3",
        "low": "4"
    }
    if priority:
        return mapping.get(priority.lower())
    else:
        return None

def parse_task(task: dict) -> ClickUpTask:
    """
    Build a ClickUpTask domain entity from a raw API task dict.

    Uses safe .get() access on every field to prevent KeyError
    when the API response has an unexpected or incomplete structure.

    Args:
        task: Raw task dictionary from ClickUp API.

    Returns:
        ClickUpTask domain entity.
    """
    assignees_raw = task.get("assignees") or []
    assignee: Optional[str] = (
            ", ".join(
                m.get("email", "")
                for m in assignees_raw
                if m.get("email")
            ) or None
    )

    status_field = task.get("status") or {}
    status: str = status_field.get("status", "")

    priority_field = task.get("priority") or {}
    priority: Optional[str] = priority_field.get("priority")

    return ClickUpTask(
        id=task.get("id", ""),
        name=task.get("name", ""),
        description=task.get("description", ""),
        status=status,
        assignee=assignee,
        priority=priority,
    )

def parse_task_with_estimation(task: dict) -> ClickUpTaskWithEstimation:
    """
    Parse a raw ClickUp task API response into a ClickUpTaskWithEstimation entity.

    Converts the time_estimate field from milliseconds to hours.

    Args:
        task: Raw task dictionary from the ClickUp API.

    Returns:
        ClickUpTaskWithEstimation domain entity.
    """
    assignees_raw = task.get("assignees") or []
    assignee: Optional[str] = (
            ", ".join(
                m.get("email", "")
                for m in assignees_raw
                if m.get("email")
            ) or None
    )

    priority_raw = task.get("priority") or {}
    priority = priority_raw.get("priority") if isinstance(priority_raw, dict) else None

    time_estimate_ms = task.get("time_estimate")
    estimation = (time_estimate_ms / 3_600_000) if time_estimate_ms else None

    return ClickUpTaskWithEstimation(
        id=task.get("id"),
        name=task.get("name", ""),
        description=task.get("description"),
        status=(task.get("status") or {}).get("status"),
        assignee=assignee,
        priority=priority,
        estimation=estimation,
    )

