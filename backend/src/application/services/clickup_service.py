import logging
from typing import List

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository


logger = logging.getLogger(__name__)


class ClickUpService:
    def __init__(self, clickup_repo: IClickUpRepository):
        self._repo = clickup_repo

    def add_space(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        logger.info("Adding new ClickUp space: space_id=%s, name=%s", space.space_id, space.name)

        result = self._repo.save(space)

        logger.info("ClickUp space added successfully: id=%s, space_id=%s", result.id, result.space_id)
        return result

    def update_space(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        logger.info("Updating ClickUp space: id=%s, space_id=%s", space.id, space.space_id)

        result = self._repo.update(space)

        logger.info("ClickUp space updated successfully: id=%s, space_id=%s", result.id, result.space_id)
        return result

    def get_by_id(self, space_id: int) -> ClickUpSpaceDTO:
        logger.info("Fetching ClickUp space by ID: id=%s", space_id)

        result = self._repo.find_by_id(space_id)

        logger.info("ClickUp space fetched successfully: id=%s, space_id=%s", result.id, result.space_id)
        return result

    def get_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        logger.info("Fetching ClickUp space by space_code: %s", space_code)

        result = self._repo.find_by_space_code(space_code)

        logger.info("ClickUp space fetched successfully: id=%s, space_id=%s", result.id, result.space_id)
        return result

    def get_all(self) -> List[ClickUpSpaceDTO]:
        logger.info("Fetching all ClickUp spaces")

        results = self._repo.find_all()

        logger.info("Fetched %s ClickUp spaces successfully", len(results))
        return results

    def get_all_light(self) -> List[ClickUpSpaceLightDTO]:
        logger.info("Fetching all ClickUp spaces (light)")

        results = self._repo.find_all_light()

        logger.info("Fetched %s ClickUp spaces (light) successfully", len(results))
        return results

    def delete(self, space_id: int) -> bool:
        logger.info("Deleting ClickUp space: id=%s", space_id)

        result = self._repo.delete(space_id)

        logger.info("ClickUp space deleted successfully: id=%s", space_id)
        return result