from fastapi import APIRouter, Depends
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container

router = APIRouter()


@router.get("/list")
def list_deployments(
    repo_url: str,
    container: Container = Depends(get_container),
) -> List[DeploymentDTO]:
    """Get all deployments for a given repo URL"""
    service = container.deployment_service
    return service.list_deployments(repo_url)