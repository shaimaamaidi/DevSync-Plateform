import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO, RepoSummary
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member_persistence_exception import MemberPersistenceException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel


logger = logging.getLogger(__name__)


def _model_to_dto(m: MemberModel) -> MemberDTO:
    repos = [RepoSummary(name=r.name, url=r.url) for r in m.repos]
    return MemberDTO(id=m.id, username=m.username, mail=m.mail, repos=repos)


def _model_to_with_repos_dto(m: MemberModel) -> MemberWithReposDTO:
    repos = [RepoSummary(name=r.name, url=r.url) for r in m.repos]
    return MemberWithReposDTO(id=m.id, username=m.username, mail=m.mail, repos=repos)


class SqlAlchemyMemberRepository(IMemberRepository):
    def __init__(self, session):
        self._session = session

    def save(self, member: MemberDTO) -> MemberDTO:
        logger.info(
            "Creating new member (username=%s, mail=%s)",
            member.username,
            member.mail
        )

        if not member.username or not member.mail:
            logger.warning(
                "Invalid input for member creation (username=%s, mail=%s)",
                member.username,
                member.mail
            )
            raise InvalidInputException(
                "Member must have a valid 'username' and 'mail' for create."
            )

        try:
            m = MemberModel(username=member.username, mail=member.mail)
            self._session.add(m)

            if member.repos:
                repo_urls = [r.url for r in member.repos]

                logger.info(
                    "Associating member with repositories (mail=%s, repo_count=%s)",
                    member.mail,
                    len(repo_urls),
                )

                repos = self._session.query(GitRepoModel).filter(GitRepoModel.url.in_(repo_urls)).all()

                m.repos = repos

            self._session.commit()
            self._session.refresh(m)

            logger.info("Member created successfully (id=%s, username=%s)", m.id, m.username)

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Member already exists (mail=%s)", member.mail)
            raise InvalidInputException("Member with this mail already exists.") from e
        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to create member (mail=%s): %s",
                member.mail,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e

    def update(self, member: MemberDTO) -> MemberDTO:
        logger.info("Updating member (id=%s)", member.id)

        if not member.id:
            logger.warning("Update failed: missing member ID")
            raise InvalidInputException("Member must have a valid database ID for update.")

        if not member.username and not member.mail and not member.repos:
            logger.warning("Update failed: no fileds provided (id=%s)", member.id)
            raise InvalidInputException(
                "Member must have a valid 'username' or 'mail' or repo's list for update."
            )

        try:
            m = self._session.query(MemberModel).filter_by(id=member.id).first()

            if not m:
                logger.warning("Member not found for update (id=%s)", member.id)
                raise MemberNotFoundException(message=f"Member not found with ID: {member.id}")

            if member.username:
                m.username = member.username
            if member.mail:
                m.mail = member.mail

            if member.repos is not None:
                repo_urls = [r.url for r in member.repos]

                logger.info(
                    "Updating member-repo associations (member_id=%s, repo_count=%s)",
                    member.id,
                    len(repo_urls),
                )

                repos = self._session.query(GitRepoModel).filter(GitRepoModel.url.in_(repo_urls)).all()

                m.repos = repos

            self._session.commit()
            self._session.refresh(m)

            logger.info(
                "Member updated successfully (id=%s)",
                m.id,
            )

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Member mail already exists (mail=%s)", member.mail)
            raise InvalidInputException("Member with this mail already exists.") from e
        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to update member (id=%s): %s",
                member.id,
                str(e),
            )
            raise MemberPersistenceException(str(e)) from e

    def find_by_id(self, member_id: int) -> MemberDTO:
        logger.info("Fetching member by id=%s", member_id)

        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()
        except Exception as e:
            logger.error(
                "Error fetching member (id=%s): %s",
                member_id,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found (id=%s)", member_id)
            raise MemberNotFoundException(message=f"Member not found with ID: {member_id}")
        
        logger.info(
            "Member fetched successfully (id=%s, username=%s, mail=%s)",
            m.id,
            m.username,
            m.mail
        )
        
        return _model_to_dto(m)

    def find_by_mail(self, mail: str) -> MemberDTO:
        logger.info("Fetching member by mail (mail=%s)", mail)

        try:
            m = self._session.query(MemberModel).filter_by(mail=mail).first()

        except Exception as e:
            logger.error(
                "Error fetching member by mail (mail=%s): %s",
                mail,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (mail=%s)", mail)
            raise MemberNotFoundException(message=f"Member not found with mail: {mail}")

        logger.info(
            "Member fetched successfully (id=%s, username=%s, mail=%s)",
            m.id,
            m.username,
            m.mail
        )
        
        return _model_to_dto(m)

    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        logger.info("Fetching members by repository ID (repo_id=%s)", repo_id)

        try:
            repo = self._session.query(GitRepoModel).filter_by(id=repo_id).first()

            if not repo:
                logger.warning("Repository not found when fetching members (repo_id=%s)", repo_id)
                return []

            members = [_model_to_dto(m) for m in repo.members]

            logger.info(
                "Members fetched successfully for repo_id=%s (count=%s)",
                repo_id,
                len(members),
            )
            
            return members

        except Exception as e:
            logger.error(
                "Failed to fetching members by repository ID (repo_id=%s): %s",
                repo_id,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e

    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        logger.info("Fetching all members with their repositories")

        try:
            rows = self._session.query(MemberModel).all()
            results = [_model_to_with_repos_dto(m) for m in rows]

            logger.info(
                "Fetched all members with repos successfully (count=%s)",
                len(results),
            )

            return results

        except MemberPersistenceException:
            raise
        except Exception as e:
            logger.error(
                "Failed to fetch members with repositories: %s",
                str(e),
            )
            raise MemberPersistenceException(str(e)) from e

    def delete(self, member_id: int) -> bool:
        logger.info("Deleting member (id=%s)", member_id)

        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()
        except Exception as e:
            logger.error(
                "Error deleting member (id=%s): %s",
                member_id,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found (id=%s)", member_id)
            raise MemberNotFoundException(message=f"Member not found with ID: {member_id}")

        try:
            self._session.delete(m)
            self._session.commit()

            logger.info("Member deleted successfully (id=%s)", m.id)

            return True

        except MemberPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to delete member (id=%s): %s",
                member_id,
                str(e)
            )
            raise MemberPersistenceException(str(e)) from e