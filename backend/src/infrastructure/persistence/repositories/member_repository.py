from typing import List

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO, RepoSummary
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member_persistence_exception import MemberPersistenceException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel


def _model_to_dto(m: MemberModel) -> MemberDTO:
    return MemberDTO(id=m.id, username=m.username, email=m.email, repo_id=m.repo_id)


class SqlAlchemyMemberRepository(IMemberRepository):
    def __init__(self, session):
        self._session = session

    def save(self, member: MemberDTO) -> MemberDTO:
        try:
            m = self._session.query(MemberModel).filter_by(email=member.email).first()
            if m:
                m.username = member.username
                m.repo_id = member.repo_id
            else:
                m = MemberModel(username=member.username, email=member.email, repo_id=member.repo_id)
                self._session.add(m)
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
            rows = self._session.query(MemberModel).filter_by(repo_id=repo_id).all()
            return [_model_to_dto(m) for m in rows]
        except Exception as e:
            raise MemberPersistenceException(str(e)) from e

    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        try:
                rows = (
                    self._session.query(MemberModel, GitRepoModel)
                    .join(GitRepoModel, MemberModel.repo_id == GitRepoModel.id)
                    .all()
                )
                acc: dict[int, MemberWithReposDTO] = {}
                for member_m, repo_m in rows:
                    if member_m.id not in acc:
                        acc[member_m.id] = MemberWithReposDTO(
                            id=member_m.id,
                            username=member_m.username,
                            email=member_m.email,
                            repos=[],
                        )
                    acc[member_m.id].repos.append(RepoSummary(name=repo_m.name, url=repo_m.url))

                orphans = self._session.query(MemberModel).filter(MemberModel.repo_id.is_(None)).all()
                for m in orphans:
                    if m.id not in acc:
                        acc[m.id] = MemberWithReposDTO(id=m.id, username=m.username, email=m.email, repos=[])

                return list(acc.values())
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