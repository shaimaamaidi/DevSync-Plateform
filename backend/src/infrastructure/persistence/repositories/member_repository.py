"""
SQLAlchemy repository for members.

This module provides a repository implementation for member persistence using SQLAlchemy ORM.
"""

import logging
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.domain.entities.member import (
    MemberCreateDTO,
    MemberDTO,
    MemberUpdateDTO,
    MemberWithReposDTO,
    RepoSummary,
    MemberCredentialsDTO,
)
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member_persistence_exception import MemberPersistenceException
from backend.src.domain.ports.repositories.i_member_repository import IMemberRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel
from backend.src.shared.helpers.password_helper import hash_password

logger = logging.getLogger(__name__)


def _model_to_dto(m: MemberModel) -> MemberDTO:
    """
    Convert a member model to a DTO.

    Args:
        m (MemberModel): Member ORM model.

    Returns:
        MemberDTO: Member DTO.
    """
    return MemberDTO(id=m.id, username=m.username, mail=m.mail)

def _model_to_with_repos_dto(m: MemberModel) -> MemberWithReposDTO:
    """
    Convert a member model to a DTO with repos.

    Args:
        m (MemberModel): Member ORM model.

    Returns:
        MemberWithReposDTO: Member DTO with repositories.
    """
    repos = [RepoSummary(name=r.name, url=r.url, id=r.id) for r in m.repos]
    return MemberWithReposDTO(id=m.id, username=m.username, mail=m.mail, repos=repos)


class SqlAlchemyMemberRepository(IMemberRepository):
    """
    SQLAlchemy implementation of IMemberRepository for member persistence.

    This repository handles CRUD operations for members using SQLAlchemy ORM.

    Attributes:
        _session (Session): SQLAlchemy session for database operations.
    """
    def __init__(self, session):
        """Initialize the repository with a session.

        Args:
            session (Session): SQLAlchemy session.
        """
        self._session = session

    def find_credentials_by_mail(self, mail: str) -> MemberCredentialsDTO:
        """
        Fetch member credentials for authentication by mail address.

        Args:
            mail (str): Member mail address.

        Returns:
            MemberCredentialsDTO: Credentials (id, mail, hashed_password) for authentication.

        Raises:
            InvalidInputException: If mail is not provided.
            MemberNotFoundException: If no member is found with the given mail.
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching credentials for authentication (mail=%s).", mail)

        if not mail or not mail.strip():
            logger.warning("Credential fetch failed: missing mail.")
            raise InvalidInputException("Mail is required.")

        try:
            m = self._session.query(MemberModel).filter_by(mail=mail).first()

        except SQLAlchemyError as e:
            logger.exception("Failed to fetch credentials (mail=%s).", mail)
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found for auth (mail=%s).", mail)
            raise MemberNotFoundException(message=f"Member not found with mail: {mail}")

        logger.info("Credentials fetched successfully (mail=%s).", mail)

        return MemberCredentialsDTO(id=m.id, mail=m.mail, hashed_password=m.password)

    def save(self, member: MemberCreateDTO) -> MemberDTO:
        """
        Create a member record.

        Args:
            member (MemberCreateDTO): Member create DTO.

        Returns:
            MemberDTO: Created member DTO.

        Raises:
            InvalidInputException: If required arguments are missing or member already exists.
            MemberPersistenceException: For database errors during persistence.
        """
        logger.info(
            "Creating new member (username=%s, mail=%s).",
            member.username,
            member.mail
        )

        if not member.username or not member.mail or not member.password:
            logger.warning(
                "Invalid input for member creation (username=%s, mail=%s).",
                member.username,
                member.mail
            )
            raise InvalidInputException(
                "Member must have a valid 'username', 'mail' and 'password' for create."
            )

        try:
            hashed_password = hash_password(member.password)

            m = MemberModel(username=member.username, mail=member.mail, password=hashed_password)
            self._session.add(m)

            self._session.commit()
            self._session.refresh(m)

            logger.info("Member created successfully (id=%s, username=%s).", m.id, m.username)

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Member already exists (mail=%s).", member.mail)
            raise InvalidInputException("Member with this mail already exists.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to create member (mail=%s).",
                member.mail
            )
            raise MemberPersistenceException(str(e)) from e

    def update(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """
        Update a member record.

        Args:
            member (MemberUpdateDTO): Member update DTO.

        Returns:
            MemberWithReposDTO: Updated member with repositories.

        Raises:
            InvalidInputException: If required arguments are missing or invalid association.
            MemberNotFoundException: If the member is not found.
            MemberPersistenceException: For database errors during update.
        """
        logger.info("Updating member (id=%s).", member.id)

        if not member.id:
            logger.warning("Update failed: missing member ID.")
            raise InvalidInputException("Member must have a valid database ID for update.")

        if not any([member.username, member.mail, member.password, member.repos]):
            logger.warning("Update failed: no fields provided (id=%s).", member.id)
            raise InvalidInputException(
                "Member must have a valid 'username' or 'mail' or 'password' or repo's list for update."
            )

        try:
            m = self._session.query(MemberModel).filter_by(id=member.id).first()

        except SQLAlchemyError as e:
            logger.exception(
                "Failed to update member (id=%s).",
                member.id
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found for update (id=%s).", member.id)
            raise MemberNotFoundException(message=f"Member not found with ID: {member.id}")

        if member.username:
            m.username = member.username

        if member.mail:
            m.mail = member.mail

        if member.password:
            hashed_password = hash_password(member.password)
            m.password = hashed_password
        if member.repos is not None:
            if not member.repos:
                logger.info(
                    "Repository list is empty; skipping repos update for member (id=%s).",
                    member.id,
                )
            else:
                if not any(r.id or r.url for r in member.repos):
                    raise InvalidInputException(
                        "Repository list must include at least one 'id' or 'url'."
                    )

                repo_ids = [r.id for r in member.repos if r.id]
                repo_urls = [r.url for r in member.repos if r.url]

                repos_from_db = []
                if not (repo_ids or repo_urls):
                    repos_from_db = []
                else:
                    query = self._session.query(GitRepoModel)

                    if repo_ids and repo_urls:
                        repos_from_db = query.filter(
                            (GitRepoModel.id.in_(repo_ids)) |
                            (GitRepoModel.url.in_(repo_urls))
                        ).all()
                    elif repo_ids:
                        repos_from_db = query.filter(GitRepoModel.id.in_(repo_ids)).all()
                    elif repo_urls:
                        repos_from_db = query.filter(GitRepoModel.url.in_(repo_urls)).all()

                repos_by_id = {r.id: r for r in repos_from_db}
                repos_by_url = {r.url: r for r in repos_from_db}

                repos = []
                missing_ids = set()
                missing_urls = set()

                for repo in member.repos:
                    repo_model = None

                    if repo.id and repo.id in repos_by_id:
                        repo_model = repos_by_id[repo.id]
                    elif repo.url and repo.url in repos_by_url:
                        repo_model = repos_by_url[repo.url]

                    if repo_model:
                        repos.append(repo_model)
                    else:
                        if repo.id:
                            missing_ids.add(repo.id)
                        if repo.url:
                            missing_urls.add(repo.url)

                if missing_ids or missing_urls:
                    missing_info = []
                    if missing_ids:
                        missing_info.append(f"ids={missing_ids}")
                    if missing_urls:
                        missing_info.append(f"urls={missing_urls}")

                    raise InvalidInputException(
                        "Repositories not found for update (%s)." % ", ".join(missing_info)
                    )

                m.repos = list({r.id: r for r in repos}.values())

                logger.info(
                    "Updating member-repo associations (member_id=%s, repo_count=%s).",
                    member.id,
                    len(m.repos),
                )
        try:
            self._session.commit()
            self._session.refresh(m)

            logger.info(
                "Member updated successfully (id=%s).",
                m.id,
            )

            return _model_to_with_repos_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Member mail already exists (mail=%s).", member.mail)
            raise InvalidInputException("Member with this mail already exists.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to update member (id=%s).",
                member.id
            )
            raise MemberPersistenceException(str(e)) from e

    def find_by_id(self, member_id: int) -> MemberDTO:
        """
        Fetch a member by id.

        Args:
            member_id (int): Member id.

        Returns:
            MemberDTO: Member DTO.

        Raises:
            MemberNotFoundException: If the member is not found.
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching member by id=%s.", member_id)

        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()

        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching member (id=%s).",
                member_id
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found (id=%s).", member_id)
            raise MemberNotFoundException(message=f"Member not found with ID: {member_id}")

        logger.info(
            "Member fetched successfully (id=%s, username=%s, mail=%s).",
            m.id,
            m.username,
            m.mail
        )

        return _model_to_dto(m)

    def find_by_mail(self, mail: str) -> MemberWithReposDTO:
        """
        Fetch a member by mail.

        Args:
            mail (str): Member mail.

        Returns:
            MemberWithReposDTO: Member with repositories DTO.

        Raises:
            MemberNotFoundException: If the member is not found.
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching member by mail (mail=%s).", mail)
        
        try:
            m = self._session.query(MemberModel).filter_by(mail=mail).first()

        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching member by mail (mail=%s).",
                mail
            )
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found (mail=%s).", mail)
            raise MemberNotFoundException(message=f"Member not found with mail: {mail}")

        logger.info(
            "Member fetched successfully (id=%s, username=%s, mail=%s).",
            m.id,
            m.username,
            m.mail
        )

        return _model_to_with_repos_dto(m)

    def find_by_repo_id(self, repo_id: int) -> List[MemberDTO]:
        """
        Fetch members by repository id.

        Args:
            repo_id (int): Repository id.

        Returns:
            List[MemberDTO]: List of member DTOs.

        Raises:
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching members by repository ID (repo_id=%s).", repo_id)

        try:
            repo = self._session.query(GitRepoModel).filter_by(id=repo_id).first()

        except SQLAlchemyError as e:
            logger.exception(
                "Failed to fetch members by repository ID (repo_id=%s).", repo_id
            )
            raise MemberPersistenceException(str(e)) from e

        if not repo:
            logger.warning("Repository not found when fetching members (repo_id=%s).", repo_id)
            raise MemberNotFoundException(message=f"Repository not found with ID: {repo_id}")

        members = [_model_to_dto(m) for m in repo.members]

        logger.info(
            "Members fetched successfully for repo_id=%s (count=%s).",
            repo_id,
            len(members),
        )

        return members

    def find_all_with_repos(self) -> List[MemberWithReposDTO]:
        """
        Fetch all members with repositories.

        Returns:
            List[MemberWithReposDTO]: List of members with repositories.

        Raises:
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching all members with their repositories.")
        
        try:
            rows = self._session.query(MemberModel).all()

        except SQLAlchemyError as e:
            logger.exception("Failed to fetch members with repositories.")
            raise MemberPersistenceException(str(e)) from e

        results = [_model_to_with_repos_dto(m) for m in rows]

        logger.info(
        "Fetched all members with repos successfully (count=%s).",
        len(results),
        )

        return results


    def delete(self, member_id: int) -> bool:
        """
        Delete a member by id.

        Args:
            member_id (int): Member id.

        Returns:
            bool: True when deletion succeeds.

        Raises:
            MemberNotFoundException: If the member is not found.
            MemberPersistenceException: For database errors during deletion.
        """
        logger.info("Deleting member (id=%s).", member_id)
        
        try:
            m = self._session.query(MemberModel).filter_by(id=member_id).first()

        except SQLAlchemyError as e:
            logger.exception("Failed to delete member (id=%s).", member_id)
            raise MemberPersistenceException(str(e)) from e

        if not m:
            logger.warning("Member not found (id=%s).", member_id)
            raise MemberNotFoundException(message=f"Member not found with ID: {member_id}")

        try:
            self._session.delete(m)
            self._session.commit()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to delete member (id=%s).", member_id)
            raise MemberPersistenceException(str(e)) from e

        logger.info("Member deleted successfully (id=%s).", m.id)

        return True