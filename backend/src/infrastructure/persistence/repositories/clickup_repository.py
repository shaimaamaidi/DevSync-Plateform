import logging
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from backend.src.domain.entities.clickup_space import (
    ClickUpRepoDTO,
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.domain.exceptions.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel


logger = logging.getLogger(__name__)


def _model_to_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDTO:
    return ClickUpSpaceDTO(id=m.id, name=m.name, space_code=m.space_code)


def _model_to_detail_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDetailDTO:
    repo = (
        ClickUpRepoDTO(id=m.repo.id, name=m.repo.name, url=m.repo.url)
        if m.repo
        else None
    )
    return ClickUpSpaceDetailDTO(
        id=m.id,
        name=m.name,
        space_code=m.space_code,
        repo=repo,
    )


def _model_to_light_dto(m: ClickUpSpaceModel) -> ClickUpSpaceLightDTO:
    repo = (
        ClickUpRepoDTO(id=m.repo.id, name=m.repo.name, url=m.repo.url)
        if m.repo
        else None
    )
    return ClickUpSpaceLightDTO(id=m.id, space_code=m.space_code, name=m.name, repo=repo)


class SqlAlchemyClickUpRepository(IClickUpRepository):
    def __init__(self, session):
        self._session = session

    def save(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        logger.info(
            "Creating ClickUp space (name=%s, space_code=%s)",
            space.name,
            space.space_code,
        )

        if not space.space_code or not space.name:
            logger.warning(
                "Invalid input for clickup space creation (name=%s, space_code=%s)",
                space.name,
                space.space_code
            )
            raise InvalidInputException(
                "ClickUp space must have a valid 'name' and 'space_code' for create."
            )

        try:
            m = ClickUpSpaceModel(name=space.name, space_code=space.space_code)
            self._session.add(m)
            self._session.commit()
            self._session.refresh(m)

            logger.info("Clickup space created successfully (name=%s, space_code=%s)",space.name, space.space_code)

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            error_code = getattr(getattr(e, "orig", None), "errno", None)
            if error_code == 1062:
                logger.warning("ClickUp space already exists (space_code=%s) in another resource", space.space_code)
                raise InvalidInputException("ClickUp space with this space_code already exists in another resource.") from e
            if error_code == 1452:
                logger.warning("Invalid repo reference for clickup space")
                raise InvalidInputException("Repository reference does not exist.") from e
            logger.error("Integrity error while creating clickup space: %s", str(e))
            raise ClickUpPersistenceException(str(e)) from e
        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to create clickup space (space_code=%s): %s",
                space.space_code,
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

    def update(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        logger.info("Updating clickup space (id=%s)", space.id)

        if not space.id:
            logger.warning("Update failed: missing clickup space ID")
            raise InvalidInputException("ClickUp space must have a valid database ID for update.")

        if not space.space_code and not space.name and not space.repo:
            logger.warning("Update failed: no fileds provided (id=%s)", space.id)
            raise InvalidInputException("ClickUp space must have a valid 'name' or 'space_code' or 'repo' for update.")

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space.id).first()

            if not m:
                logger.warning("Clickup space not found for update (id=%s)", space.id)
                raise ClickUpSpaceNotFoundException(message=f"ClickUp space not found with ID: {space.id}")

            if space.name:
                m.name = space.name
            if space.space_code:
                m.space_code = space.space_code
            if space.repo is not None:
                if not space.repo.id and not space.repo.url:
                    raise InvalidInputException("Repo must include 'id' or 'url' for update.")

                repo_model = None
                if space.repo.id:
                    repo_model = (
                        self._session.query(GitRepoModel)
                        .filter(GitRepoModel.id == space.repo.id)
                        .first()
                    )

                if not repo_model and space.repo.url:
                    repo_model = (
                        self._session.query(GitRepoModel)
                        .filter(GitRepoModel.url == space.repo.url)
                        .first()
                    )

                if not repo_model:
                    raise InvalidInputException("Repository reference does not exist.")

                if repo_model.clickup_space and repo_model.clickup_space.id != m.id:
                    raise InvalidInputException(
                        "Repository is already associated with another ClickUp space."
                    )

                m.repo = repo_model

            self._session.commit()
            self._session.refresh(m)

            logger.info(
                "Clickup space updated successfully (id=%s)",
                m.id,
            )

            return _model_to_detail_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            error_code = getattr(getattr(e, "orig", None), "errno", None)
            if error_code == 1062:
                logger.warning("ClickUp space already exists (space_code=%s) in another resource", space.space_code)
                raise InvalidInputException("ClickUp space with this space_code already exists in another resource.") from e
            if error_code == 1452:
                logger.warning("Invalid repo reference for clickup space")
                raise InvalidInputException("Repository reference does not exist.") from e
            logger.error("Integrity error while updating clickup space: %s", str(e))
            raise ClickUpPersistenceException(str(e)) from e
        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to update clickup space (id=%s): %s",
                space.id,
                str(e),
            )
            raise ClickUpPersistenceException(str(e)) from e

    def find_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        logger.info("Fetching clickup space by id=%s", space_id)

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        except Exception as e:
            logger.error(
                "Error fetching clickup space (id=%s): %s",
                space_id,
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

        if not m:
            logger.warning("Clickup space not found (id=%s)", space_id)
            raise ClickUpSpaceNotFoundException(message=f"ClickUp space not found with ID: {space_id}")

        logger.info(
            "ClickUp space fetched successfully (id=%s, name=%s, space_code=%s)",
            m.id,
            m.name,
            m.space_code
        )

        return _model_to_detail_dto(m)

    def find_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        logger.info("Fetching clickup space by space ID (space_code=%s)", space_code)

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(space_code=space_code).first()
        except Exception as e:
            logger.error(
                "Error fetching clickup space by space code (space_code=%s): %s",
                space_code,
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

        if not m:
            logger.warning("Clickup space not found (space_code=%s)", space_code)
            raise ClickUpSpaceNotFoundException(message=f"ClickUp space not found with SPACE_CODE: {space_code}")

        logger.info(
            "ClickUp space fetched successfully (id=%s, name=%s, space_code=%s)",
            m.id,
            m.name,
            m.space_code
        )

        return _model_to_dto(m)

    def find_all(self) -> List[ClickUpSpaceDTO]:
        logger.info("Fetching all clickup spaces")

        try:
            results = [_model_to_dto(m) for m in self._session.query(ClickUpSpaceModel).all()]

            logger.info(
                "Fetched all ClickUp spaces successfully (count=%s)",
                len(results),
            )

            return results

        except Exception as e:
            logger.error(
                "Error fetching all clickup spaces: %s",
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        logger.info("Fetching all clickup spaces (light)")

        try:
            rows = (
                self._session.query(ClickUpSpaceModel)
                .options(joinedload(ClickUpSpaceModel.repo))
                .all()
            )

            logger.info(
                "Fetched (light) all ClickUp spaces successfully (count=%s)",
                len(rows),
            )

            return [_model_to_light_dto(r) for r in rows]

        except Exception as e:
            logger.error(
                "Error fetching all clickup spaces (light): %s",
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

    def delete(self, space_id: int) -> bool:
        logger.info("Deleting clickup space (id=%s)", space_id)

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        except Exception as e:
            logger.error(
                "Error deleting clickup space (id=%s): %s",
                space_id,
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e

        if not m:
            logger.warning("Clickup Space not found (id=%s)", space_id)
            raise ClickUpSpaceNotFoundException(message=f"ClickUp space not found with ID: {space_id}")

        try:
            self._session.delete(m)
            self._session.commit()

            logger.info("Clickup Space deleted successfully (id=%s)", m.id)

            return True

        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to delete clickup space (id=%s): %s",
                space_id,
                str(e)
            )
            raise ClickUpPersistenceException(str(e)) from e
