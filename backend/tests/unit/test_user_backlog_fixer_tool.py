"""
Unit tests for UserBacklogFixerTool.
"""

import json
from unittest.mock import MagicMock

import pytest

from backend.src.domain.entities.backlog.backlog_structure import BacklogStructure, EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.epic import Epic
from backend.src.domain.entities.backlog.task import Task
from backend.src.domain.entities.backlog.user_story import UserStory
from backend.src.domain.exceptions.tool.invalid_tool_argument_exception import InvalidToolArgumentException
from backend.src.domain.exceptions.tool.tool_execution_exception import ToolExecutionException
from backend.src.infrastructure.external.backlog_generation.tools.user_backlog_fixer_tool import (
    UserBacklogFixerTool,
)


def _backlog() -> BacklogStructure:
    return BacklogStructure(
        epics=[
            EpicBacklog(
                epic=Epic(title="Sales", description="Sales workflows"),
                user_stories=[
                    UserStoryWithTasks(
                        user_story=UserStory(title="Track leads", description="As a user..."),
                        tasks=[Task(title="Create lead", description="Implement create")],
                    )
                ],
            )
        ]
    )


def _backlog_json() -> str:
    return _backlog().model_dump_json()


@pytest.mark.asyncio
async def test_user_backlog_fixer_tool_success() -> None:
    """
    Tool fixes backlog and returns JSON.
    """
    fixer = MagicMock()
    fixer.fix_user_backlog.return_value = _backlog()

    tool = UserBacklogFixerTool(fixer)
    result = await tool(_backlog_json(), _backlog_json())

    parsed = json.loads(result)
    assert parsed["epics"][0]["epic"]["title"] == "Sales"
    fixer.fix_user_backlog.assert_called_once()


@pytest.mark.asyncio
async def test_user_backlog_fixer_tool_invalid_reference() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid reference JSON.
    """
    tool = UserBacklogFixerTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool("not-json", _backlog_json())


@pytest.mark.asyncio
async def test_user_backlog_fixer_tool_invalid_user_backlog() -> None:
    """
    Tool raises InvalidToolArgumentException on invalid user backlog JSON.
    """
    tool = UserBacklogFixerTool(MagicMock())

    with pytest.raises(InvalidToolArgumentException):
        await tool(_backlog_json(), "not-json")


@pytest.mark.asyncio
async def test_user_backlog_fixer_tool_wraps_error() -> None:
    """
    Tool wraps unexpected errors into ToolExecutionException.
    """
    fixer = MagicMock()
    fixer.fix_user_backlog.side_effect = RuntimeError("fail")

    tool = UserBacklogFixerTool(fixer)

    with pytest.raises(ToolExecutionException):
        await tool(_backlog_json(), _backlog_json())
