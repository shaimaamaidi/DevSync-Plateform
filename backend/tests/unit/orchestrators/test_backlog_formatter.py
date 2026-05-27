"""
Unit tests for backlog formatter.
"""

from backend.src.domain.entities.backlog.structure import BacklogStructure, EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.task import Task
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_backlog


def test_format_backlog_basic_structure() -> None:
    """
    format_backlog should include epic, user story, and task lines.
    """
    backlog = BacklogStructure(
        epics=[
            EpicBacklog(
                epic=Epic(title="Epic", description="Desc"),
                user_stories=[
                    UserStoryWithTasks(
                        user_story=UserStory(title="Story", description="Story desc"),
                        tasks=[Task(title="Task", description="Task desc")],
                    )
                ],
            )
        ]
    )

    result = format_backlog(backlog)

    assert "EPIC: Epic" in result
    assert "USER STORY: Story" in result
    assert "- Task: Task desc" in result
