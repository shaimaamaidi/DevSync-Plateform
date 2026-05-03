"""
Domain helpers for resolving ClickUp assignees and task priorities.

This module defines utility functions used to map human-readable assignee names
and priority labels into ClickUp-compatible identifiers. It handles mapping
between assignee identifiers and ClickUp workspace members.
"""

import logging
from typing import List, Dict

from backend.src.domain.exceptions.clickup.clickup_assignee_email_not_found_exception import \
    AssigneeEmailNotInClickUpException


logger = logging.getLogger(__name__)


def resolve_assignee_ids_strict(
        name_to_email: dict,
        email_to_id: Dict[str, int],
        assignee_names: List[str],
        ignore_mails: bool
) -> List[int]:
    """
    Resolve assignee names to ClickUp member IDs.

    This function converts assignee names into ClickUp user IDs using
    provided mapping dictionaries. If some assignees cannot be resolved,
    behavior depends on the `ignore_mails` flag.

    Args:
        name_to_email (dict): Mapping of assignee names to email addresses.
        email_to_id (Dict[str, int]): Mapping of email addresses to ClickUp member IDs.
        assignee_names (List[str]): List of assignee names to resolve.
        ignore_mails (bool):
            If True, unresolved assignees are ignored.
            If False, an exception is raised when resolution fails.

    Returns:
        List[int]: List of resolved ClickUp member IDs.

    Raises:
        AssigneeEmailNotInClickUpException: If some assignees cannot be resolved and ignore_mails=False.
    """
    logger.info(
        "Starting assignee resolution (strict). input_count=%d.",
        len(assignee_names),
    )

    resolved = []
    unresolved_emails = []

    for name in assignee_names:
        if not name or name == "غير محدد":
            logger.warning("Skipping invalid assignee name: '%s'.", name)
            continue

        mail = name_to_email.get(name.lower())

        if not mail:
            logger.warning("No email mapping found for assignee name: '%s'.", name)
            unresolved_emails.append(name)
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

    if unresolved_emails and not ignore_mails:
        raise AssigneeEmailNotInClickUpException(unresolved_emails)

    logger.info(
        "Assignee resolution (strict): %d/%d resolved.",
        len(resolved),
        len([n for n in assignee_names if n and n != "غير محدد"]),
    )

    return resolved


def priority_to_int(priority: str) -> int:
    """
    Convert a priority label to a numeric ranking.

    This function normalizes ClickUp priority labels into a numeric scale
    where lower values represent higher priority.

    Args:
        priority: Priority label (e.g., "urgent", "high", "normal", "low").

    Returns:
        int: Numeric priority rank (1 = highest, 4 = lowest).
    """
    mapping = {
        "urgent": 1,
        "high": 2,
        "normal": 3,
        "low": 4
    }
    return mapping.get(priority.lower(), 3)