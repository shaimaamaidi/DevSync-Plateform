import logging

from fastapi import APIRouter, Depends
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO
from backend.src.infrastructure.di.container import Container
from backend.src.presentation.api.deps import get_container


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/")
def get_all_spaces(container: Container = Depends(get_container)):
    logger.info("[ClickUp] Fetching all ClickUp spaces")

    service = container.clickup_service
    results = service.get_all()

    logger.info("[ClickUp] Retrieved %d ClickUp spaces", len(results))
    return results

@router.get("/light")
def get_all_light(container: Container = Depends(get_container)):
    logger.info("[ClickUp] Fetching all ClickUp spaces (light version)")

    service = container.clickup_service
    results = service.get_all_light()

    logger.info("[ClickUp] Retrieved %d ClickUp spaces (light)", len(results))
    return results

@router.get("/{space_id}")
def get_space_by_id(space_id: int, container: Container = Depends(get_container)):
    logger.info("[ClickUp] Fetching ClickUp space by id=%s", space_id)

    service = container.clickup_service
    result = service.get_by_id(space_id)

    logger.info("[ClickUp] ClickUp space retrieved successfully: id=%s", space_id)
    return result

@router.post("/")
def create_space(space: ClickUpSpaceDTO, container: Container = Depends(get_container)):
    logger.info(
        "[ClickUp] Creating ClickUp space: space_id=%s, name=%s",
        space.space_code,
        space.name,
    )

    service = container.clickup_service
    result = service.add_space(space)

    logger.info(
        "[ClickUp] ClickUp space created successfully: space_code=%s",
        result.space_code,
    )
    return result

@router.put("/{space_id}")
def update_space(space_id: int, space: ClickUpSpaceDTO, container: Container = Depends(get_container)):
    logger.info(
        "[ClickUp] Updating ClickUp space: id=%s",
        space_id,
    )

    service = container.clickup_service
    space.id = space_id
    result = service.update_space(space)

    logger.info(
        "[ClickUp] ClickUp space updated successfully: id=%s",
        space_id,
    )
    return result

@router.delete("/{space_id}")
def delete_space(space_id: int, container: Container = Depends(get_container)):
    logger.info("[ClickUp] Deleting ClickUp space: id=%s", space_id)

    service = container.clickup_service
    result = service.delete(space_id)

    logger.info("[ClickUp] ClickUp space deleted successfully: id=%s", space_id)
    return result