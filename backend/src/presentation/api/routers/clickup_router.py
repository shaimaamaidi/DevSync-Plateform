from fastapi import APIRouter, Depends
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container

router = APIRouter()


@router.get("/")
def get_all_spaces(container: Container = Depends(get_container)):
    service = container.clickup_service
    return service.get_all()


@router.get("/light")
def get_all_light(container: Container = Depends(get_container)):
    service = container.clickup_service
    return service.get_all_light()


@router.get("/{space_id}")
def get_space_by_id(space_id: int, container: Container = Depends(get_container)):
    service = container.clickup_service
    return service.get_by_id(space_id)


@router.post("/")
def create_space(space: ClickUpSpaceDTO, container: Container = Depends(get_container)):
    service = container.clickup_service
    return service.add_space(space)


@router.put("/{space_id}")
def update_space(space_id: int, space: ClickUpSpaceDTO, container: Container = Depends(get_container)):
    service = container.clickup_service
    space.id = space_id
    return service.update_space(space)


@router.delete("/{space_id}")
def delete_space(space_id: int, container: Container = Depends(get_container)):
    service = container.clickup_service
    return service.delete(space_id)