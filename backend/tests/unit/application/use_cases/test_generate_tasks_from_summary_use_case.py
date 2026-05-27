"""
Unit tests for GenerateTasksFromSummaryUseCase.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.src.application.use_cases.generate_tasks_from_summary_use_case import GenerateTasksFromSummaryUseCase


def test_generate_tasks_from_meeting_summary_returns_empty_list_when_generator_returns_none() -> None:
    """
    Test that the summary use case normalizes a missing generator result to an empty list.
    """
    clickup_reader = MagicMock()
    clickup_reader.get_space_structure_metadata.return_value = [
        SimpleNamespace(
            id="folder-1",
            name="Backend",
            lists=[
                SimpleNamespace(
                    id="list-1",
                    name="Sprint",
                    statuses=["Open"],
                    priorities=["High"],
                    tasks=[],
                )
            ],
        )
    ]

    task_generator = MagicMock()
    task_generator.generate_tasks.return_value = None

    use_case = GenerateTasksFromSummaryUseCase(clickup_reader, task_generator)

    result = use_case.generate_tasks_from_meeting_summary("summary text", "space-1")

    clickup_reader.get_space_structure_metadata.assert_called_once_with("space-1")
    task_generator.generate_tasks.assert_called_once_with(
        meeting_summary="summary text",
        locations_statuses={
            "Backend / Sprint": {
                "statuses": ["Open"],
                "priorities": ["High"],
            }
        },
    )
    assert result == []