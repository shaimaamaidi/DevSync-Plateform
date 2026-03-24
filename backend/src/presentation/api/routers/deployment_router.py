from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.deployment import DeploymentDTO

router = APIRouter()


@router.get("/list")
def list_deployments(repo_url: str, request: Request) -> List[DeploymentDTO]:
    """Get all deployments for a given repo URL"""
    service = request.app.state.container.deployment_service
    return service.list_deployments(repo_url)