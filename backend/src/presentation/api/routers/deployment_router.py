import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/list")
def list_deployments(
    repo_url: str,
    container: Container = Depends(get_container),
) -> List[DeploymentDTO]:
    """Get all deployments for a given repo URL"""
    logger.info(
        "[Deployment] Fetching deployments for repository: repo_url=%s.",
        repo_url,
    )

    service = container.deployment_service
    results = service.list_deployments(repo_url)

    logger.info(
        "[Deployment] Retrieved %d deployments for repo_url=%s.",
        len(results),
        repo_url,
    )
    return results