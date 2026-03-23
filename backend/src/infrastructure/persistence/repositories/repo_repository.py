from typing import List, Optional

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, MemberSummary, ClickUpSpaceSummary
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel


def _model_to_dto(m: GitRepoModel) -> GitRepoDTO:
    return GitRepoDTO(id=m.id, name=m.name, url=m.url)


def _model_to_detail_dto(m: GitRepoModel) -> GitRepoDetailDTO:
    members = [MemberSummary(username=mb.username, email=mb.email) for mb in m.members]
    space = ClickUpSpaceSummary(name=m.clickup_space.name) if m.clickup_space else None
    return GitRepoDetailDTO(id=m.id, name=m.name, url=m.url, members=members, clickup_space=space)


class SqlAlchemyRepoRepository(IRepoRepository):
    def __init__(self, session):
        self._session = session

    def save(self, repo: GitRepoDTO) -> GitRepoDTO:
        m = self._session.query(GitRepoModel).filter_by(url=repo.url).first()
        if m:
            m.name = repo.name
        else:
            m = GitRepoModel(name=repo.name, url=repo.url)
            self._session.add(m)
        self._session.commit()
        self._session.refresh(m)
        return _model_to_dto(m)

    def find_by_id(self, repo_id: int) -> Optional[GitRepoDTO]:
        m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        return _model_to_dto(m) if m else None

    def find_by_url(self, url: str) -> Optional[GitRepoDTO]:
        m = self._session.query(GitRepoModel).filter_by(url=url).first()
        return _model_to_dto(m) if m else None

    def find_by_name(self, name: str) -> Optional[GitRepoDTO]:
        m = self._session.query(GitRepoModel).filter_by(name=name).first()
        return _model_to_dto(m) if m else None

    def find_all(self) -> List[GitRepoDTO]:
        return [_model_to_dto(m) for m in self._session.query(GitRepoModel).all()]

    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        return [_model_to_detail_dto(m) for m in self._session.query(GitRepoModel).all()]

    def delete(self, repo_id: int) -> bool:
        m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        if not m:
            return False
        self._session.delete(m)
        self._session.commit()
        return True