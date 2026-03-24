from fastapi import APIRouter, Request
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO

router = APIRouter()


@router.post("/space")
def associate_space(request: Request, repo: GitRepoDTO, clickup_space: ClickUpSpaceDTO):
    service = request.app.state.container.associator_service
    return service.associate_space(repo, clickup_space)


@router.post("/members")
def associate_members(request: Request, repo: GitRepoDTO, members: List[dict]):
    service = request.app.state.container.associator_service
    return service.associate_members(repo, members)