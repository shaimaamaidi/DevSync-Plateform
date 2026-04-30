"""
Domain helpers for resolving ClickUp assignees and task priorities.

This module defines utility functions used to map human-readable assignee names
and priority labels into ClickUp-compatible identifiers. It handles fuzzy matching
between external data sources (e.g., Excel) and ClickUp workspace members.
"""

import logging
from difflib import SequenceMatcher
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


def resolve_assignee_ids(name_to_email: dict, email_to_id: Dict[str, int], assignee_names: List[str]) -> List[int]:
    """
    Resolve assignee names to ClickUp member IDs.

    This function maps human-readable assignee names to ClickUp user IDs using
    intermediate email resolution and fuzzy matching against external data sources.

    Args:
        name_to_email: Mapping of usernames to emails from external source (e.g., Excel).
        email_to_id: Mapping of email addresses to ClickUp member IDs.
        assignee_names: List of assignee display names to resolve.

    Returns:
        List[int]: List of resolved ClickUp member IDs.
    """
    logger.info(
        "Starting assignee resolution. input_count=%d.",
        len(assignee_names),
    )

    resolved = []
    for name in assignee_names:
        if not name or name == "غير محدد":
            logger.debug("Skipping invalid assignee name: '%s'.", name)
            continue

        member_id = _find_member_id(name, name_to_email, email_to_id)

        if member_id:
            resolved.append(member_id)
        else:
            logger.warning("Member '%s' not found in workspace.", name)

    logger.info(
        "Assignee resolution: %d/%d resolved.",
        len(resolved),
        len([n for n in assignee_names if n and n != "غير محدد"]),
    )

    return resolved


def _find_member_id(name: str, name_to_email: dict, email_to_id: Dict[str, int]) -> Optional[int]:
    """
    Resolve a single assignee name to a ClickUp member ID.

    This function performs a two-step resolution:
    1. Fuzzy match the provided name against external username mappings.
    2. Use the resolved email to retrieve the ClickUp member ID.

    Args:
        name: Assignee display name.
        name_to_email: Mapping of usernames to emails from external source.
        email_to_id: Mapping of email addresses to ClickUp member IDs.

    Returns:
        Optional[int]: ClickUp member ID if resolved, otherwise None.
    """
    logger.info("Resolving member. name='%s'.", name)

    # Step 1 — find the email via Excel (similarity match on the name)
    best_email = None
    best_score = 0.0

    for username, email in name_to_email.items():
        score = SequenceMatcher(None, name.lower(), username.lower()).ratio()
        if score > best_score:
            best_score = score
            best_email = email

    if best_score < 0.5 or not best_email:
        logger.warning(
            "No Excel match for '%s' (best score: %.2f).",
            name,
            best_score,
        )
        return None

    logger.info(
        "Excel match: '%s' → email='%s' (score: %.2f).",
        name,
        best_email,
        best_score,
    )

    # Step 2 — find the ClickUp ID via the email
    member_id = email_to_id.get(best_email.lower())
    if not member_id:
        logger.warning(
            "Email '%s' matched for '%s' but not found in ClickUp workspace.",
            best_email,
            name,
        )
        return None

    logger.info("Resolved: '%s' → ClickUp ID %s.", name, member_id)

    return member_id

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
