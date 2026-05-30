"""
ClickUp space task reader API routes.

This module defines API endpoints for retrieving the complete task
structure of a ClickUp space, including folders, lists, and tasks.

Routes:
    GET /{space_id}: Retrieve all folders, lists, and tasks for a space.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, status

from backend.src.application.use_cases.read_clickup_space_task_use_case import ReadClickUpSpaceTaskUseCase
from backend.src.domain.entities.clickup.folder_with_lists import FolderWithListsAndEstimation
from backend.src.presentation.api.deps import get_read_clickup_space_task_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/{space_id}",
    response_model=List[FolderWithListsAndEstimation],
    status_code=status.HTTP_200_OK,
    summary="Get ClickUp space tasks",
    description="Retrieve all folders, lists, and tasks for a given ClickUp space.",
)
def get_tasks_by_space(
    space_id: str,
    use_case: ReadClickUpSpaceTaskUseCase = Depends(get_read_clickup_space_task_use_case),
) -> List[FolderWithListsAndEstimation]:
    """
    Retrieve the complete task structure of a ClickUp space.

    Args:
        space_id (str): ClickUp space identifier (path param).
        use_case (ReadClickUpSpaceTaskUseCase): Injected use case.

    Returns:
        List[FolderWithListsAndEstimation]: Folders with their lists and tasks.
    """
    logger.info("Fetching ClickUp space tasks: space_id=%s.", space_id)

    results = use_case.get_tasks_by_space(space_id)

    logger.info(
        "Fetched ClickUp space tasks successfully: space_id=%s, folders_count=%s.",
        space_id,
        len(results),
    )

    return results