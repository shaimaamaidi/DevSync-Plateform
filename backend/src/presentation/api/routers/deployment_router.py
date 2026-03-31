"""
Deployment API routes.

This module defines API endpoints for listing deployments associated with a repository.

Routes:
    GET /list: List deployments for a repository URL.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/list")
async def list_deployments(
    repo_url: str,
    container: Container = Depends(get_container),
) -> List[DeploymentDTO]:
    """
    List deployments for a repository URL.

    Args:
        repo_url (str): The repository URL to fetch deployments for.
        container (Container): Dependency injection container.

    Returns:
        List[DeploymentDTO]: List of deployments for the repository.
    """
    logger.info(
        "Fetching deployments for repository: repo_url=%s.",
        repo_url,
    )

    service = container.deployment_service
    results = await service.list_deployments(repo_url)

    logger.info(
        "Retrieved %d deployments for repo_url=%s.",
        len(results),
        repo_url,
    )

    return results