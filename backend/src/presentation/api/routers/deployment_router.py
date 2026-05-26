"""
Deployment API routes.

This module defines API endpoints for listing deployments associated with a repository.

Routes:
    GET /list: List deployments for a repository URL.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.ports.input.i_deployment_use_case import IDeploymentUseCase
from backend.src.presentation.api.deps import get_deployment_use_case


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get(
    "/list",
    response_model=List[DeploymentDTO],
    status_code=status.HTTP_200_OK,
    summary="List deployments for a repository",
    description=(
        "Retrieves all deployments associated with a given repository URL. "
        "Used to track deployment history and environments."
    )
)
async def list_deployments(
    repo_url: str,
    use_case: IDeploymentUseCase = Depends(get_deployment_use_case),
) -> List[DeploymentDTO]:
    """
    List deployments for a repository URL.

    Args:
        repo_url (str): The repository URL to fetch deployments for.
        use_case (IDeploymentUseCase): Dependency injection container.

    Returns:
        List[DeploymentDTO]: List of deployments for the repository.
    """
    logger.info(
        "Fetching deployments for repository: repo_url=%s.",
        repo_url,
    )

    results = await use_case.list_deployments(repo_url)

    logger.info(
        "Retrieved %d deployments for repo_url=%s.",
        len(results),
        repo_url,
    )

    return results