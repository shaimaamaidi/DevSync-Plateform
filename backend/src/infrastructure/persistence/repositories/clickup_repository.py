from typing import List

from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO
from backend.src.domain.exceptions.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel


def _model_to_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDTO:
    return ClickUpSpaceDTO(id=m.id, name=m.name, space_id=m.space_id, repo_id=m.repo_id)


def _model_to_light_dto(m: ClickUpSpaceModel) -> ClickUpSpaceLightDTO:
    return ClickUpSpaceLightDTO(id=m.id, space_id=m.space_id, name=m.name)


class SqlAlchemyClickUpRepository(IClickUpRepository):
    def __init__(self, session):
        self._session = session

    def save(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        if not space.space_id or not space.name:
            raise InvalidInputException(
                "ClickUp space must have a valid 'name' and 'space_id' for create."
            )

        try:
            m = ClickUpSpaceModel(name=space.name, space_id=space.space_id, repo_id=space.repo_id)
            self._session.add(m)
            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise ClickUpPersistenceException(str(e)) from e

    def update(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        if not space.id:
            raise InvalidInputException("ClickUp space must have a valid database ID for update.")

        if not space.space_id and not space.name and not space.repo_id:
            raise InvalidInputException("ClickUp space must have a valid 'name' or 'space_id' or 'repo_id' for update.")

        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space.id).first()
            if not m:
                raise ClickUpSpaceNotFoundException(space.id)
            if space.name:
                m.name = space.name
            if space.space_id:
                m.space_id = space.space_id
            if space.repo_id:
                m.repo_id = space.repo_id
            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise ClickUpPersistenceException(str(e)) from e

    def find_by_id(self, space_id: int) -> ClickUpSpaceDTO:
        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        except Exception as e:
            raise ClickUpPersistenceException(str(e)) from e
        if not m:
            raise ClickUpSpaceNotFoundException(space_id)
        return _model_to_dto(m)

    def find_by_space_id(self, space_id: str) -> ClickUpSpaceDTO:
        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(space_id=space_id).first()
        except Exception as e:
            raise ClickUpPersistenceException(str(e)) from e
        if not m:
            raise ClickUpSpaceNotFoundException(space_id)
        return _model_to_dto(m)

    def find_all(self) -> List[ClickUpSpaceDTO]:
        try:
            return [_model_to_dto(m) for m in self._session.query(ClickUpSpaceModel).all()]
        except Exception as e:
            raise ClickUpPersistenceException(str(e)) from e

    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        try:
            rows = self._session.query(
                ClickUpSpaceModel.id,
                ClickUpSpaceModel.space_id,
                ClickUpSpaceModel.name,
            ).all()
            return [ClickUpSpaceLightDTO(id=r.id, space_id=r.space_id, name=r.name) for r in rows]
        except Exception as e:
            raise ClickUpPersistenceException(str(e)) from e

    def delete(self, space_id: int) -> bool:
        try:
            m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        except Exception as e:
            raise ClickUpPersistenceException(str(e)) from e
        if not m:
            raise ClickUpSpaceNotFoundException(space_id)
        try:
            self._session.delete(m)
            self._session.commit()
            return True
        except ClickUpPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise ClickUpPersistenceException(str(e)) from e