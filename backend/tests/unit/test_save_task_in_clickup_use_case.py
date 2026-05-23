"""
Unit tests for SaveSummaryTasksInClickUpUseCase.
"""

from unittest.mock import MagicMock

from backend.src.application.use_cases.save_summary_tasks_use_case import SaveSummaryTasksInClickUpUseCase
from backend.src.domain.entities.verified_tasks.verified_task_from_summary import VerifiedTaskFromSummary


def _verified_task() -> VerifiedTaskFromSummary:
    return VerifiedTaskFromSummary(
        action="create",
        task_name="Build login",
        task_description="Implement login flow",
        task_assigne="Alice",
        task_status="To Do",
        task_priority="High",
        location="Backend",
    )


def test_save_to_clickup_resolves_members_and_applies_results() -> None:
    clickup_task_service = MagicMock()
    clickup_task_service.get_space_structure.return_value = ["folder"]
    clickup_task_service.get_workspace_members.return_value = [{"id": 1, "name": "Alice"}]

    member_repo = MagicMock()
    member_repo.find_by_arabic_name.return_value = {"Alice": "alice@example.com"}

    clickup_writer = MagicMock()

    use_case = SaveSummaryTasksInClickUpUseCase(
        clickup_task_service=clickup_task_service,
        member_repo=member_repo,
        clickup_writer=clickup_writer,
    )

    use_case.save_to_clickup(
        tasks=[_verified_task()],
        space_id="space-1",
        ignore_names=False,
        ignore_mails=True,
    )

    clickup_task_service.get_space_structure.assert_called_once_with("space-1")
    clickup_task_service.invalidate.assert_called_once_with("space-1")
    member_repo.find_by_arabic_name.assert_called_once_with(["Alice"], False)
    clickup_task_service.get_workspace_members.assert_called_once_with("space-1")
    clickup_writer.apply_results.assert_called_once()
    apply_args = clickup_writer.apply_results.call_args.args
    assert apply_args[0][0].task_name == "Build login"


def test_save_to_clickup_skips_member_lookup_when_no_assignees() -> None:
    clickup_task_service = MagicMock()
    clickup_task_service.get_space_structure.return_value = []

    member_repo = MagicMock()
    clickup_writer = MagicMock()

    use_case = SaveSummaryTasksInClickUpUseCase(
        clickup_task_service=clickup_task_service,
        member_repo=member_repo,
        clickup_writer=clickup_writer,
    )

    task = _verified_task()
    task.task_assigne = "غير محدد"

    use_case.save_to_clickup(
        tasks=[task],
        space_id="space-1",
        ignore_names=True,
        ignore_mails=False,
    )

    member_repo.find_by_arabic_name.assert_not_called()
    clickup_task_service.get_workspace_members.assert_not_called()
    clickup_writer.apply_results.assert_called_once()
