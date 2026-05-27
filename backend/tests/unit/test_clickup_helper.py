"""
Unit tests for ClickUp helper utilities.
"""

import pytest

from backend.src.domain.exceptions.clickup.clickup_assignee_email_not_found_exception import AssigneeEmailNotInClickUpException
from backend.src.domain.exceptions.clickup.clickup_assignee_name_not_found_exception import AssigneeNameNotFoundException
from backend.src.infrastructure.external.clickup.helpers.clickup_helper import (
    parse_task,
    priority_to_str,
    resolve_assignee_ids_from_mails,
    resolve_assignee_ids_strict,
)


def test_priority_to_str_maps_known_priorities() -> None:
    """
    Test that priority labels are normalized to ClickUp ranks.
    """
    assert priority_to_str("urgent") == "1"
    assert priority_to_str("high") == "2"
    assert priority_to_str("normal") == "3"
    assert priority_to_str("low") == "4"
    assert priority_to_str(None) is None


def test_parse_task_builds_clickup_task() -> None:
    """
    Test that a raw task dict is converted into a ClickUpTask entity.
    """
    task = parse_task(
        {
            "id": "task-1",
            "name": "Build login",
            "description": "Implement login flow",
            "status": {"status": "done"},
            "assignees": [{"email": "alice@example.com"}, {"email": "bob@example.com"}],
            "priority": {"priority": "high"},
        }
    )

    assert task.id == "task-1"
    assert task.status == "done"
    assert task.assignee == "alice@example.com, bob@example.com"
    assert task.priority == "high"


def test_resolve_assignee_ids_from_mails_handles_strict_and_ignore_modes() -> None:
    """
    Test assignee mail resolution with and without ignoring missing entries.
    """
    email_to_id = {"alice@example.com": 11}

    assert resolve_assignee_ids_from_mails(email_to_id, ["alice@example.com"], ignore_mails=False) == [11]

    with pytest.raises(AssigneeEmailNotInClickUpException):
        resolve_assignee_ids_from_mails(email_to_id, ["missing@example.com"], ignore_mails=False)

    assert resolve_assignee_ids_from_mails(email_to_id, ["missing@example.com"], ignore_mails=True) == []


def test_resolve_assignee_ids_strict_handles_missing_names_and_emails() -> None:
    """
    Test assignee name resolution including missing names and unresolved emails.
    """
    name_to_email = {"alice": "alice@example.com"}
    email_to_id = {"alice@example.com": 11}

    assert resolve_assignee_ids_strict(name_to_email, email_to_id, ["alice"], ignore_names=False, ignore_mails=False) == [11]

    with pytest.raises(AssigneeNameNotFoundException):
        resolve_assignee_ids_strict({}, email_to_id, ["bob"], ignore_names=False, ignore_mails=False)

    with pytest.raises(AssigneeEmailNotInClickUpException):
        resolve_assignee_ids_strict({"bob": "bob@example.com"}, email_to_id, ["bob"], ignore_names=True, ignore_mails=False)
