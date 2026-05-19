"""
SQLAlchemy repository for ClickUp spaces.

This module provides a repository implementation for ClickUp space persistence using SQLAlchemy ORM.
"""

import logging
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from backend.src.domain.entities.clickup_space import (
    ClickUpRepoDTO,
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.domain.exceptions.clickup.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel


logger = logging.getLogger(__name__)


def _model_to_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDTO:
    """
    Convert a ClickUp space model to a DTO.

    Args:
        m (ClickUpSpaceModel): ClickUp space ORM model.

    Returns:
        ClickUpSpaceDTO: ClickUp space DTO.
    """
    return ClickUpSpaceDTO(id=m.id, name=m.name, space_code=m.space_code)

def _model_to_detail_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDetailDTO:
    """
    Convert a ClickUp space model to a detailed DTO.

    Args:
        m (ClickUpSpaceModel): ClickUp space ORM model.

    Returns:
        ClickUpSpaceDetailDTO: ClickUp space detail DTO.
    """
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
    """
    Convert a ClickUp space model to a light DTO.

    Args:
        m (ClickUpSpaceModel): ClickUp space ORM model.

    Returns:
        ClickUpSpaceLightDTO: lickUp space light DTO.
    """
    repo = (
        ClickUpRepoDTO(id=m.repo.id, name=m.repo.name, url=m.repo.url)
        if m.repo
        else None
    )

    return ClickUpSpaceLightDTO(id=m.id, space_code=m.space_code, name=m.name, repo=repo)


class SqlAlchemyClickUpRepository(IClickUpRepository):
    """
    SQLAlchemy implementation of IClickUpRepository for ClickUp space persistence.

    This repository handles CRUD operations for ClickUp spaces using SQLAlchemy ORM.

    Attributes:
        _session (Session): SQLAlchemy session for database operations.
    """

    def __init__(self, session):
        """
        Initialize the repository with a session.

        Args:
            session (Session): SQLAlchemy session.
        """
        self._session = session

    def save(self, space: ClickUpSpaceCreateDTO) -> ClickUpSpaceDTO:
        """
        Create a ClickUp space record.

        Args:
            space (ClickUpSpaceCreateDTO): ClickUp space create DTO.

        Returns:
            ClickUpSpaceDTO: Created ClickUp space DTO.

        Raises:
            InvalidInputException: If required arguments are missing or space already exists.
            ClickUpPersistenceException: For database errors during persistence.
        """
        logger.info(
            "Creating Click up space (name=%s, space_code=%s).",
        
            space.name,
            space.space_code,
        )

        if not space.space_code or not space.name:
            logger.warning(
                "Invalid input for click up space creation (name=%s, space_code=%s).",
                space.name,
                space.space_code
            )
            raise InvalidInputException(
                "Click up space must have a valid 'name' and 'space_code' for create."
            )

        try:
            m = ClickUpSpaceModel(name=space.name, space_code=space.space_code)
            self._session.add(m)
            self._session.commit()
            self._session.refresh(m)

            logger.info("Click up space created successfully (name=%s, space_code=%s).",space.name, space.space_code)

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Click up space already exists (space_code=%s) in another resource.", space.space_code or "N/A")
            raise InvalidInputException("Click up space with this space_code already exists in another resource.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to create click up space (space_code=%s).",
                space.space_code
            )
            raise ClickUpPersistenceException() from e

    def update(self, space: ClickUpSpaceUpdateDTO) -> ClickUpSpaceDetailDTO:
        """
        Update a ClickUp space record.

        Args:
            space (ClickUpSpaceUpdateDTO): ClickUp space update DTO.

        Returns:
            ClickUpSpaceDetailDTO: Updated ClickUp space detail DTO.

        Raises:
            InvalidInputException:
                - If required arguments are missing.
                - If no fields are provided for update.
                - If repository reference is invalid (missing id/url, not found, or already linked).
            ClickUpSpaceNotFoundException: If the ClickUp space is not found.
            ClickUpPersistenceException: For database errors during update.
        """
        logger.info("Updating click up space (id=%s).", space.id)

        if not space.id:
            logger.warning("Update failed: missing click up space ID.")
            raise InvalidInputException("ClickUp space must have a valid database ID for update.")

        if not space.space_code and not space.name and not space.repo:
            logger.warning("Update failed: no fields provided (id=%s).", space.id)
            raise InvalidInputException("Please provide at least one field to update.")

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space.id).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to update click up space (id=%s).",
                space.id
            )
            raise ClickUpPersistenceException() from e

        if not m:
            logger.warning("Click up space not found for update (id=%s).", space.id)
            raise ClickUpSpaceNotFoundException(message="ClickUp space not found.")

        if space.name:
            m.name = space.name

        if space.space_code:
            m.space_code = space.space_code

        if space.repo is not None:
            if not (space.repo.id or space.repo.url):
                raise InvalidInputException("Repository must include 'id' or 'url' for update.")

            try:
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
            except SQLAlchemyError as e:
                self._session.rollback()
                logger.exception(
                    "Failed to fetch repository reference during click up space update (id=%s).",
                    space.id
                )
                raise ClickUpPersistenceException() from e

            if not repo_model:
                raise InvalidInputException("Repository reference does not exist.")

            if repo_model.clickup_space and repo_model.clickup_space.id != m.id:
                raise InvalidInputException(
                    "Repository is already associated with another Click up space."
                )

            m.repo = repo_model

        try:
            self._session.flush()
            self._session.commit()
            m = (
                self._session.query(ClickUpSpaceModel)
                .options(joinedload(ClickUpSpaceModel.repo))
                .filter_by(id=m.id)
                .first()
            )

            logger.info(
                "Click up space updated successfully (id=%s).",
                m.id,
            )

            return _model_to_detail_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Click up space already exists (space_code=%s) in another resource.", space.space_code)
            raise InvalidInputException("Click up space with this space_code already exists in another resource.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to update click up space (id=%s).",
                space.id
            )
            raise ClickUpPersistenceException() from e


    def find_by_id(self, space_id: int) -> ClickUpSpaceDetailDTO:
        """
        Fetch a ClickUp space by id.

        Args:
            space_id (int): ClickUp space id.

        Returns:
            ClickUpSpaceDetailDTO: ClickUp space detail DTO.

        Raises:
            InvalidInputException: If space_id is not provided.
            ClickUpSpaceNotFoundException: If the ClickUp space is not found.
            ClickUpPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching click up space by id=%s.", space_id)

        if not space_id:
            logger.warning(
                "Invalid input for click up space fetch by id (id=%s).",
                space_id
            )
            raise InvalidInputException(
                "ClickUp space must have a valid 'id' for fetch by id."
            )

        try:
            m = (
                self._session.query(ClickUpSpaceModel)
                .options(joinedload(ClickUpSpaceModel.repo))
                .filter_by(id=space_id)
                .first()
            )

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching clickup space (id=%s).",
                space_id
            )
            raise ClickUpPersistenceException() from e

        if not m:
            logger.warning("Click up space not found (id=%s).", space_id)
            raise ClickUpSpaceNotFoundException(message="ClickUp space not found.")

        logger.info(
            "ClickUp space fetched successfully (id=%s, name=%s, space_code=%s).",
            m.id,
            m.name,
            m.space_code
        )

        return _model_to_detail_dto(m)

    def find_by_space_code(self, space_code: str) -> ClickUpSpaceDTO:
        """
        Fetch a ClickUp space by space code.

        Args:
            space_code (str): ClickUp space code.

        Returns:
            ClickUpSpaceDTO: ClickUp space DTO.

        Raises:
            InvalidInputException: If space_code is not provided.
            ClickUpSpaceNotFoundException: If the ClickUp space is not found.
            ClickUpPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching click up space by space ID (space_code=%s).", space_code)

        if not space_code:
            logger.warning(
                "Invalid input for click up space fetch by space code (space_code=%s).",
                space_code
            )
            raise InvalidInputException(
                "Click up space must have a valid 'space_code' for fetch."
            )

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(space_code=space_code).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching click up space by space code (space_code=%s).",
                space_code
            )
            raise ClickUpPersistenceException() from e

        if not m:
            logger.warning("Click up space not found (space_code=%s).", space_code)
            raise ClickUpSpaceNotFoundException(message=f"ClickUp space not found with SPACE_ID: {space_code}")

        logger.info(
            "Click up space fetched successfully (id=%s, name=%s, space_code=%s).",
            m.id,
            m.name,
            m.space_code
        )

        return _model_to_dto(m)

    def find_by_name(self, name: str) -> ClickUpSpaceDTO | None:
        """
        Fetch a ClickUp space by name, returns None if not found.
        Used for existence checks before creation.

        Args:
            name (str): ClickUp space name.

        Returns:
            ClickUpSpaceDTO | None: ClickUp space DTO or None if not found.

        Raises:
            InvalidInputException: If name is not provided.
            ClickUpPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching click up space by name=%s.", name)

        if not name:
            raise InvalidInputException("Click up space must have a valid 'name' for fetch by name.")

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Error fetching click up space by name=%s.", name)
            raise ClickUpPersistenceException() from e

        return _model_to_dto(m) if m else None

    def find_all(self) -> List[ClickUpSpaceDTO]:
        """
        Return all ClickUp spaces.

        Returns:
            List[ClickUpSpaceDTO]: List of ClickUp space DTOs.

        Raises:
            ClickUpPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching all click up spaces.")

        try:
            results = [_model_to_dto(m) for m in self._session.query(ClickUpSpaceModel).all()]

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching all click up spaces."
            )
            raise ClickUpPersistenceException() from e

        logger.info(
            "Fetched all Click up spaces successfully (count=%s).",
            len(results),
        )

        return results

    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        """
        Return all ClickUp spaces in light form.

        Returns:
            List[ClickUpSpaceLightDTO]: List of ClickUp space light DTOs.

        Raises:
            ClickUpPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching all click up spaces (light).")

        try:
            rows = (
                self._session.query(ClickUpSpaceModel)
                .options(joinedload(ClickUpSpaceModel.repo))
                .all()
            )

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching all click up spaces (light)."
            )
            raise ClickUpPersistenceException() from e

        logger.info(
            "Fetched (light) all click up spaces successfully (count=%s).",
            len(rows),
        )

        return [_model_to_light_dto(r) for r in rows]

    def delete(self, space_id: int) -> bool:
        """
        Delete a ClickUp space by id.

        Args:
            space_id (int): ClickUp space id.

        Returns:
            bool: True when deletion succeeds.

        Raises:
            InvalidInputException: If space_id is not provided.
            ClickUpSpaceNotFoundException: If the ClickUp space is not found.
            ClickUpPersistenceException: For database errors during deletion.
        """
        logger.info("Deleting click up space (id=%s).", space_id)

        if not space_id:
            logger.warning(
                "Invalid input for click up space delete (id=%s).",
                space_id
            )
            raise InvalidInputException(
                "ClickUp space must have a valid 'id' for delete."
            )

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error deleting click up space (id=%s).",
                space_id
            )
            raise ClickUpPersistenceException() from e

        if not m:
            logger.warning("Click up Space not found (id=%s).", space_id)
            raise ClickUpSpaceNotFoundException(message="ClickUp space not found.")

        try:
            self._session.delete(m)
            self._session.commit()

            logger.info("Click up Space deleted successfully (id=%s).", m.id)

            return True

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to delete click up space (id=%s).",
                space_id
            )
            raise ClickUpPersistenceException() from e
