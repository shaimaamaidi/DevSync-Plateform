from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO

router = APIRouter()


@router.post("/space")
def associate_space(request: Request, repo: GitRepoDTO, space_name: str, space_id: str):
    service = request.app.state.container.associator_service
    return service.associate_space(repo, space_name, space_id)


@router.post("/members")
def associate_members(request: Request, repo: GitRepoDTO, members: List[dict]):
    service = request.app.state.container.associator_service
    return service.associate_members(repo, members)