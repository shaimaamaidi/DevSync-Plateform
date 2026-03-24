from fastapi import APIRouter, Request
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO

router = APIRouter()


@router.get("/")
def get_all_spaces(request: Request):
    service = request.app.state.container.clickup_service
    return service.get_all()


@router.get("/light")
def get_all_light(request: Request):
    service = request.app.state.container.clickup_service
    return service.get_all_light()


@router.get("/{space_id}")
def get_space_by_id(space_id: int, request: Request):
    service = request.app.state.container.clickup_service
    return service.get_by_id(space_id)


@router.post("/")
def create_space(request: Request, space: ClickUpSpaceDTO):
    service = request.app.state.container.clickup_service
    return service.add_space(space)


@router.put("/{space_id}")
def update_space(space_id:int, request: Request, space: ClickUpSpaceDTO):
    service = request.app.state.container.clickup_service
    space.id = space_id
    return service.update_space(space)


@router.delete("/{space_id}")
def delete_space(space_id: int, request: Request):
    service = request.app.state.container.clickup_service
    return service.delete(space_id)