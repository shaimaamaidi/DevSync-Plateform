from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO, RepoSummary
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member_persistence_exception import MemberPersistenceException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel


def _model_to_dto(m: MemberModel) -> MemberDTO:
    repos = [RepoSummary(name=r.name, url=r.url) for r in m.repos]
    return MemberDTO(id=m.id, username=m.username, email=m.email, repos=repos)


def _model_to_with_repos_dto(m: MemberModel) -> MemberWithReposDTO:
    repos = [RepoSummary(name=r.name, url=r.url) for r in m.repos]
    return MemberWithReposDTO(id=m.id, username=m.username, email=m.email, repos=repos)


class SqlAlchemyMemberRepository(IMemberRepository):
    def __init__(self, session):
        self._session = session

    def save(self, member: MemberDTO) -> MemberDTO:
        if not member.username or not member.email:
            raise InvalidInputException(
                "Member must have a valid 'username' and 'email' for create."
            )
        try:
            m = MemberModel(username=member.username, email=member.email)
            self._session.add(m)

            if member.repos:
                repo_urls = [r.url for r in member.repos]
                repos = self._session.query(GitRepoModel).filter(GitRepoModel.url.in_(repo_urls)).all()
                m.repos = repos

            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise MemberPersistenceException(str(e)) from e

    def update(self, member: MemberDTO) -> MemberDTO:
        if not member.id:
            raise InvalidInputException("Member must have a valid database ID for update.")

        if not member.username and not member.email and not member.repos:
            raise InvalidInputException(
                "Member must have a valid 'username' or 'email' or repo's list for update."
            )

        try:
            m = self._session.query(MemberModel).filter_by(id=member.id).first()
            if not m:
                raise MemberNotFoundException(member.id)
            if member.username:
                m.username = member.username
            if member.email:
                m.email = member.email

            if member.repos is not None:
                repo_urls = [r.url for r in member.repos]
                repos = self._session.query(GitRepoModel).filter(GitRepoModel.url.in_(repo_urls)).all()
                m.repos = repos

            self._session.commit()
            self._session.refresh(m)
            return _model_to_dto(m)
        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise MemberPersistenceException(str(e)) from e

    def find_by_id(self, member_id: int) -> MemberDTO:
        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e
        if not m:
            raise MemberNotFoundException(member_id)
        return _model_to_dto(m)

    def find_by_email(self, email: str) -> MemberDTO:
        try:
            m = self._session.query(MemberModel).filter_by(email=email).first()
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e
        if not m:
            raise MemberNotFoundException(email)
        return _model_to_dto(m)

    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        try:
            repo = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
            if not repo:
                return []
            return [_model_to_dto(m) for m in repo.members]
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e

    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        try:
            rows = self._session.query(MemberModel).all()
            return [_model_to_with_repos_dto(m) for m in rows]
        except MemberPersistenceException:
            raise
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e

    def delete(self, member_id: int) -> bool:
        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e
        if not m:
            raise MemberNotFoundException(member_id)
        try:
            self._session.delete(m)
            self._session.commit()
            return True
        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            raise MemberPersistenceException(str(e)) from e