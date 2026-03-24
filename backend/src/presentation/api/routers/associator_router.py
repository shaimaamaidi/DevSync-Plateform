from fastapi import APIRouter, Depends
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container

router = APIRouter()


@router.post("/space")
def associate_space(
    repo: GitRepoDTO,
    clickup_space: ClickUpSpaceDTO,
    container: Container = Depends(get_container),
):
    service = container.associator_service
    return service.associate_space(repo, clickup_space)


@router.post("/members")
def associate_members(
    repo: GitRepoDTO,
    members: List[dict],
    container: Container = Depends(get_container),
):
    service = container.associator_service
    return service.associate_members(repo, members)