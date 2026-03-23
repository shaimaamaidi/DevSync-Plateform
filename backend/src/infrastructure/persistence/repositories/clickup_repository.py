from typing import List, Optional

from src.domain.entities.clickup_space import ClickUpSpaceDTO, ClickUpSpaceLightDTO
from src.domain.ports.repositories.i_clickup_repository import IClickUpRepository
from src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel


def _model_to_dto(m: ClickUpSpaceModel) -> ClickUpSpaceDTO:
    return ClickUpSpaceDTO(id=m.id, name=m.name, space_id=m.space_id, repo_id=m.repo_id)


def _model_to_light_dto(m: ClickUpSpaceModel) -> ClickUpSpaceLightDTO:
    return ClickUpSpaceLightDTO(id=m.id, space_id=m.space_id, name=m.name)


class SqlAlchemyClickUpRepository(IClickUpRepository):
    def __init__(self, session):
        self._session = session

    def save(self, space: ClickUpSpaceDTO) -> ClickUpSpaceDTO:
        m = self._session.query(ClickUpSpaceModel).filter_by(space_id=space.space_id).first()
        if m:
            m.name = space.name
            m.repo_id = space.repo_id
        else:
            m = ClickUpSpaceModel(name=space.name, space_id=space.space_id, repo_id=space.repo_id)
            self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return _model_to_dto(m)

    def find_by_id(self, space_id: int) -> Optional[ClickUpSpaceDTO]:
        m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        return _model_to_dto(m) if m else None

    def find_by_space_id(self, space_id: str) -> Optional[ClickUpSpaceDTO]:
        m = self._session.query(ClickUpSpaceModel).filter_by(space_id=space_id).first()
        return _model_to_dto(m) if m else None

    def find_all(self) -> List[ClickUpSpaceDTO]:
        return [_model_to_dto(m) for m in self._session.query(ClickUpSpaceModel).all()]

    def find_all_light(self) -> List[ClickUpSpaceLightDTO]:
        rows = self._session.query(
            ClickUpSpaceModel.id,
            ClickUpSpaceModel.space_id,
            ClickUpSpaceModel.name,
        ).all()
        return [ClickUpSpaceLightDTO(id=r.id, space_id=r.space_id, name=r.name) for r in rows]

    def delete(self, space_id: int) -> bool:
        m = self._session.query(ClickUpSpaceModel).filter_by(id=space_id).first()
        if not m:
            return False
        self._session.delete(m)
        self._session.commit()
        return True