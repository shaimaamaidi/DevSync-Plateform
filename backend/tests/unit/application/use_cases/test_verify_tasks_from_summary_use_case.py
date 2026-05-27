"""
Unit tests for VerifyTasksFromSummaryUseCase.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.src.application.use_cases.verify_tasks_from_summary_use_case import VerifyTasksFromSummaryUseCase
from backend.src.domain.entities.generated_tasks.generated_task_from_summary import GeneratedTaskFromSummary
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask


def test_verify_tasks_returns_create_results_when_space_has_no_tasks() -> None:
    """
    Test that generated summary tasks are mapped directly when the ClickUp space is empty.
    """
    clickup_reader = MagicMock()
    clickup_reader.get_space_full_structure.return_value = [
        SimpleNamespace(
            id="folder-1",
            name="Backend",
            lists=[
                SimpleNamespace(
                    id="list-1",
                    name="Sprint",
                    tasks=[],
                    statuses=[],
                    priorities=[],
                )
            ],
        )
    ]

    task_verifier = MagicMock()
    member_repo = MagicMock()
    use_case = VerifyTasksFromSummaryUseCase(clickup_reader, task_verifier, member_repo)
    generated_tasks = [
        GeneratedTaskFromSummary(
            task_name="Task 1",
            task_description="Do the work",
            task_assigne="Alice",
            task_status="Open",
            task_priority="High",
            location="Backend / Sprint",
        )
    ]

    result = use_case.verify_tasks(generated_tasks, "space-1")

    assert result == [
        VerifiedTaskFromSummary(
            action="create",
            task_name="Task 1",
            task_description="Do the work",
            task_assigne="Alice",
            task_status="Open",
            task_priority="High",
            location="Backend / Sprint",
            task_id=None,
        )
    ]
    member_repo.find_by_mails.assert_not_called()
    task_verifier.verify_tasks.assert_not_called()


def test_verify_tasks_groups_existing_tasks_and_resolves_assignees() -> None:
    """
    Test that the summary use case resolves assignee emails before verification.
    """
    existing_task = ClickUpTask(
        id="task-1",
        name="Existing task",
        description="Existing work",
        status="Open",
        assignee="alice@example.com, bob@example.com",
        priority="High",
    )
    clickup_reader = MagicMock()
    clickup_reader.get_space_full_structure.return_value = [
        SimpleNamespace(
            id="folder-1",
            name="Backend",
            lists=[
                SimpleNamespace(
                    id="list-1",
                    name="Sprint",
                    tasks=[existing_task],
                    statuses=["Open"],
                    priorities=["High"],
                )
            ],
        )
    ]

    member_repo = MagicMock()
    member_repo.find_by_mails.return_value = {
        "alice@example.com": "Alice",
        "bob@example.com": "Bob",
    }

    expected_verified = [
        VerifiedTaskFromSummary(
            action="update",
            task_name="Generated task",
            task_description="Updated work",
            task_assigne="Alice, Bob",
            task_status="Open",
            task_priority="High",
            location="Backend / Sprint",
            task_id="task-1",
        )
    ]
    task_verifier = MagicMock()
    task_verifier.verify_tasks.return_value = expected_verified

    use_case = VerifyTasksFromSummaryUseCase(clickup_reader, task_verifier, member_repo)
    generated_tasks = [
        GeneratedTaskFromSummary(
            task_name="Generated task",
            task_description="Updated work",
            task_assigne="Alice",
            task_status="Open",
            task_priority="High",
            location="Backend / Sprint",
        )
    ]

    result = use_case.verify_tasks(generated_tasks, "space-1")

    assert result == expected_verified
    assert set(member_repo.find_by_mails.call_args.args[0]) == {
        "alice@example.com",
        "bob@example.com",
    }
    task_verifier.verify_tasks.assert_called_once()
    assert task_verifier.verify_tasks.call_args.kwargs["existing_tasks"][0].assignee == "Alice, Bob"
    assert task_verifier.verify_tasks.call_args.kwargs["tasks"] == generated_tasks