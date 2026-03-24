from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, MemberSummary, ClickUpSpaceSummary
from backend.src.domain.entities.member import RepoSummary
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo_persistence_exception import RepoPersistenceException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel


def _model_to_dto(m: GitRepoModel) -> GitRepoDTO:
    members = [
        MemberSummary(
            username=mb.username,
            email=mb.email,
            repos=[RepoSummary(name=r.name, url=r.url) for r in mb.repos]
        )
        for mb in m.members
    ]
    return GitRepoDTO(id=m.id, name=m.name, url=m.url, members=members)


def _model_to_detail_dto(m: GitRepoModel) -> GitRepoDetailDTO:
    members = [
        MemberSummary(
            username=mb.username,
            email=mb.email,
            repos=[RepoSummary(name=r.name, url=r.url) for r in mb.repos]
        )
        for mb in m.members
    ]
    space = (
        ClickUpSpaceSummary(name=m.clickup_space.name, space_id=m.clickup_space.space_id)
        if m.clickup_space
        else None
    )
    return GitRepoDetailDTO(id=m.id, name=m.name, url=m.url, members=members, clickup_space=space)

class SqlAlchemyRepoRepository(IRepoRepository):
    def __init__(self, session):
        self._session = session

    def save(self, repo: GitRepoDTO) -> GitRepoDTO:
        if not repo.name or not repo.url:
            raise InvalidInputException(
                "GitHub Repo must have a valid 'name' and 'url' for create."
            )
        try:
            m = GitRepoModel(name=repo.name, url=repo.url)
            self._session.add(m)
            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise RepoPersistenceException(str(e)) from e

    def update(self, repo: GitRepoDTO) -> GitRepoDTO:
        if not repo.id:
            raise InvalidInputException("GitHub Repo must have a valid database ID for update.")

        if not repo.name and not repo.url:
            raise InvalidInputException(
                "GitHub Repo must have a valid 'name' or 'url' for update."
            )

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo.id).first()
            if not m:
                raise RepoNotFoundException(repo.id)
            if repo.name:
                m.name = repo.name
            if repo.url:
                m.url = repo.url
            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise RepoPersistenceException(str(e)) from e

    def find_by_id(self, repo_id: int) -> GitRepoDTO:
        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e
        if not m:
            raise RepoNotFoundException(repo_id)
        return _model_to_dto(m)

    def find_by_url(self, url: str) -> GitRepoDTO:
        try:
            m = self._session.query(GitRepoModel).filter_by(url=url).first()
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e
        if not m:
            raise RepoNotFoundException(url)
        return _model_to_dto(m)

    def find_by_name(self, name: str) -> GitRepoDTO:
        try:
            m = self._session.query(GitRepoModel).filter_by(name=name).first()
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e
        if not m:
            raise RepoNotFoundException(name)
        return _model_to_dto(m)

    def find_all(self) -> List[GitRepoDTO]:
        try:
            return [_model_to_dto(m) for m in self._session.query(GitRepoModel).all()]
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e

    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        try:
            return [_model_to_detail_dto(m) for m in self._session.query(GitRepoModel).all()]
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e

    def delete(self, repo_id: int) -> bool:
        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        except Exception as e:
            raise RepoPersistenceException(str(e)) from e
        if not m:
            raise RepoNotFoundException(repo_id)
        try:
            self._session.delete(m)
            self._session.commit()
            return True
        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise RepoPersistenceException(str(e)) from e