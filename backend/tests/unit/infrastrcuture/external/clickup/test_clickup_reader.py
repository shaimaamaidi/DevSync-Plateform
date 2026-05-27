"""
Unit tests for the ClickUp reader adapter.
"""

from datetime import timezone
from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.clickup.clickup_client_exception import ClickUpClientException
from backend.src.domain.exceptions.clickup.clickup_resource_not_found_exception import ClickUpResourceNotFoundException
from backend.src.domain.exceptions.clickup.clickup_workspace_members_exception import ClickUpWorkspaceMembersException
from backend.src.infrastructure.external.clickup.clickup_reader import ClickUpReader


def test_space_exists_returns_space_name() -> None:
    """
    Test that the reader returns the ClickUp space name when the space exists.
    """
    http_client = MagicMock()
    http_client.get.return_value = {"name": "Platform"}
    reader = ClickUpReader(http_client)

    result = reader.space_exists("space-1")

    assert result == "Platform"
    http_client.get.assert_called_once_with("/space/space-1")


def test_space_exists_raises_not_found_when_api_client_fails() -> None:
    """
    Test that the reader maps ClickUp client failures to a not found exception.
    """
    http_client = MagicMock()
    http_client.get.side_effect = ClickUpClientException("boom")
    reader = ClickUpReader(http_client)

    with pytest.raises(ClickUpResourceNotFoundException):
        reader.space_exists("space-1")


def test_get_workspace_members_filters_invalid_and_non_assignable_entries() -> None:
    """
    Test that only assignable and complete workspace members are returned.
    """
    http_client = MagicMock()
    http_client.get.return_value = {
        "teams": [
            {
                "members": [
                    {"user": {"id": 1, "username": "alice", "email": "alice@example.com", "role": 20}},
                    {"user": {"id": 2, "username": "bob", "email": "bob@example.com", "role": 40}},
                    {"user": {"id": 3, "username": "guest", "email": "guest@example.com", "role": 80}},
                    {"user": {"id": 4, "username": "broken", "email": None, "role": 60}},
                ]
            }
        ]
    }
    reader = ClickUpReader(http_client)

    result = reader.get_workspace_members()

    assert result == [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"},
    ]
    http_client.get.assert_called_once_with("/team")


def test_ms_to_dt_converts_milliseconds_to_utc_datetime() -> None:
    """
    Test that ClickUp millisecond timestamps are converted to UTC datetimes.
    """
    dt = ClickUpReader._ms_to_dt("1704067200000")

    assert dt is not None
    assert dt.tzinfo == timezone.utc
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 1


def test_get_task_by_id_returns_parsed_task(monkeypatch) -> None:
    """
    Test that the reader returns the parsed task when the API call succeeds.
    """
    http_client = MagicMock()
    http_client.get.return_value = {"id": "task-1", "name": "Build login"}
    reader = ClickUpReader(http_client)

    monkeypatch.setattr(
        "backend.src.infrastructure.external.clickup.clickup_reader.parse_task",
        lambda payload: payload,
    )

    result = reader.get_task_by_id("task-1")

    assert result == {"id": "task-1", "name": "Build login"}
    http_client.get.assert_called_once_with("/task/task-1")


def test_get_workspace_members_with_roles_returns_roles() -> None:
    """
    Test that the reader returns members with their roles.
    """
    http_client = MagicMock()
    http_client.get.return_value = {
        "teams": [
            {
                "members": [
                    {"user": {"id": 1, "email": "alice@example.com", "role": 20}},
                    {"user": {"id": 2, "email": "bob@example.com", "role": 40}},
                ]
            }
        ]
    }
    reader = ClickUpReader(http_client)

    result = reader.get_workspace_members_with_roles()

    assert result == [
        {"id": 1, "email": "alice@example.com", "role": "owner"},
        {"id": 2, "email": "bob@example.com", "role": "admin"},
    ]


def test_get_workspace_members_with_roles_raises_when_empty() -> None:
    """
    Test that the reader raises when no workspace members can be found.
    """
    http_client = MagicMock()
    http_client.get.return_value = {"teams": [{"members": []}]}
    reader = ClickUpReader(http_client)

    with pytest.raises(ClickUpWorkspaceMembersException):
        reader.get_workspace_members_with_roles()