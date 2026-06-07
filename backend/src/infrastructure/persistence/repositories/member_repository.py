"""
SQLAlchemy repository for members.

This module provides a repository implementation for member persistence using SQLAlchemy ORM.
"""

import logging
from typing import List, Dict

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.domain.entities.member import (
    MemberCreateDTO,
    MemberDTO,
    MemberUpdateDTO,
    MemberWithReposDTO,
    RepoSummary,
    MemberCredentialsDTO,
)
from backend.src.domain.exceptions.clickup.clickup_assignee_name_not_found_exception import \
    AssigneeNameNotFoundException
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.member.member_not_found_exception import MemberNotFoundException
from backend.src.domain.exceptions.member.member_persistence_exception import MemberPersistenceException
from backend.src.domain.exceptions.repo.repo_not_found_exception import RepoNotFoundException
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
    return MemberDTO(
        id=m.id,
        username=m.username,
        arabic_name=m.arabic_name,
        mail=m.mail,
        role=m.role
    )

def _model_to_with_repos_dto(m: MemberModel) -> MemberWithReposDTO:
    """
    Convert a member model to a DTO with repos.

    Args:
        m (MemberModel): Member ORM model.

    Returns:
        MemberWithReposDTO: Member DTO with repositories.
    """
    repos = []

    if m.repos:
        repos = [RepoSummary(name=r.name, url=r.url, id=r.id) for r in m.repos if r is not None]

    return MemberWithReposDTO(
        id=m.id,
        username=m.username,
        arabic_name=m.arabic_name,
        role=m.role,
        mail=m.mail,
        repos=repos
    )


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
            MemberNotFoundException: If no member is found with the given mail.
            MemberPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching credentials for authentication (mail=%s).", mail)

        try:
            m = self._session.query(MemberModel).filter_by(mail=mail).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to fetch credentials (mail=%s).", mail)
            raise MemberPersistenceException() from e 

        if not m:
            logger.warning("Member not found for auth (mail=%s).", mail)
            raise MemberNotFoundException(message="No account found with this email address.")

        logger.info("Credentials fetched successfully (mail=%s).", mail)

        return MemberCredentialsDTO(
            id=m.id,
            mail=m.mail,
            role=m.role,
            hashed_password=m.password
        )

    def save(self, member: MemberCreateDTO) -> MemberDTO:
        """
        Create a member record.

        Args:
            member (MemberCreateDTO): Member create DTO.

        Returns:
            MemberDTO: Created member DTO.

        Raises:
            MemberPersistenceException: For database errors during persistence.
        """
        logger.info(
            "Creating new member (username=%s, arabic_name=%s, role=%s, mail=%s).",
            member.username,
            member.arabic_name,
            member.role,
            member.mail,
        )

        try:
            hashed_password = hash_password(member.password)

            m = MemberModel(
                username=member.username,
                mail=member.mail,
                arabic_name=member.arabic_name,
                role=member.role,
                password=hashed_password
            )
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
            raise MemberPersistenceException() from e 

    def update(self, member: MemberUpdateDTO) -> MemberWithReposDTO:
        """
        Update a member record.

        Args:
            member (MemberUpdateDTO): Member update DTO.

        Returns:
            MemberWithReposDTO: Updated member with repositories.

        Raises:
            MemberNotFoundException: If the member is not found.
            MemberPersistenceException: For database errors during update.
            InvalidInputException:
                - If repository list is invalid (missing id/url).
                - If one or more repositories do not exist.
                - If member mail already exists.
        """
        logger.info("Updating member (id=%s).", member.id)

        try:
            m = self._session.query(MemberModel).filter_by(id=member.id).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to update member (id=%s).",
                member.id
            )
            raise MemberPersistenceException() from e 

        if not m:
            logger.warning("Member not found for update (id=%s).", member.id)
            raise MemberNotFoundException(message="Member not found.")

        if member.username:
            m.username = member.username

        if member.arabic_name:
            m.arabic_name = member.arabic_name

        if member.mail:
            m.mail = member.mail

        if member.role:
            m.role = member.role

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
                invalid_repos = [r for r in member.repos if not r.id and not r.url]
                if invalid_repos:
                    raise InvalidInputException("Each repository must include at least one 'id' or 'url'.")

                repo_ids = [r.id for r in member.repos if r.id]
                repo_urls = [r.url for r in member.repos if r.url]
                query = self._session.query(GitRepoModel)

                if repo_ids and repo_urls:
                    repos_from_db = query.filter(
                        (GitRepoModel.id.in_(repo_ids)) | (GitRepoModel.url.in_(repo_urls))
                    ).all()
                elif repo_ids:
                    repos_from_db = query.filter(GitRepoModel.id.in_(repo_ids)).all()
                else:
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
                        "Some of the selected repositories could not be found. Please verify and try again."
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
            raise MemberPersistenceException() from e 

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
            self._session.rollback()
            logger.exception(
                "Error fetching member (id=%s).",
                member_id
            )
            raise MemberPersistenceException() from e 

        if not m:
            logger.warning("Member not found (id=%s).", member_id)
            raise MemberNotFoundException(message="Member not found.")

        logger.info(
            "Member fetched successfully (id=%s, username=%s, arabic_name=%s, mail=%s).",
            m.id,
            m.username,
            m.arabic_name,
            m.mail
        )

        return _model_to_dto(m)

    def find_by_arabic_name(self, arabic_names: list[str], ignore_names:bool = False) -> Dict[str, str]:
        """
        Fetch members by their Arabic names and return a mapping to their emails.

        This method resolves a list of Arabic names into a dictionary mapping
        normalized names to email addresses. If some names cannot be resolved,
        behavior depends on the `ignore_names` flag.

        Args:
            arabic_names (list[str]): List of Arabic names to resolve into members.
            ignore_names (bool):
                If True, unresolved names are ignored.
                If False, an exception is raised when some names are not found.

        Returns:
            Dict[str, str]: Mapping of normalized Arabic name to member email.

        Raises:
            AssigneeNameNotFoundException: If one or more Arabic names are not found and ignore_names=False.
            MemberPersistenceException: If a database error occurs during the query.
        """
        logger.info("Fetching members by arabic names.")

        resolved: Dict[str, str] = {}
        unresolved = []

        try:
            for name in arabic_names:
                m = self._session.query(MemberModel).filter_by(arabic_name=name).first()
                if not m:
                    logger.warning("Member not found (arabic_name=%s).", name)
                    unresolved.append(name)
                else:
                    name =name.lower()
                    mail = m.mail.lower()
                    resolved[name] = mail
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching members by arabic names."
            )
            raise MemberPersistenceException() from e 

        if unresolved and not ignore_names:
            raise AssigneeNameNotFoundException(unresolved)

        logger.info(
            "Members fetched successfully by arabic names.",
        )

        return resolved

    def find_by_mails(self, mails: list[str]) -> Dict[str, str]:
        """
        Fetch members by their mails and return a mapping to their arabic names.

        This method resolves a list of mails into a dictionary mapping
        normalized mail to arabic names. If some names cannot be resolved,
        then we ignore them.

        Args:
            mails (list[str]): List of mails to resolve into members.

        Returns:
            Dict[str, str]: Mapping of normalized mails to arabic names.

        Raises:
            MemberPersistenceException: If a database error occurs during the query.
        """
        logger.info("Fetching members by arabic names.")

        if not mails:
            logger.warning(
                "Invalid input for member fetching by arabic names (List provided is empty)."
            )
            return {}

        resolved: Dict[str, str] = {}

        try:
            for mail in mails:
                m = self._session.query(MemberModel).filter_by(mail=mail).first()
                if not m:
                    logger.warning("Member not found (mail=%s).", mail)
                else:
                    name = m.arabic_name
                    mail = mail.lower()
                    resolved[mail] = name
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Error fetching members by arabic names."
            )
            raise MemberPersistenceException() from e 

        logger.info(
            "Members fetched successfully by arabic names.",
        )

        return resolved

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
            self._session.rollback()
            logger.exception(
                "Error fetching member by mail (mail=%s).",
                mail
            )
            raise MemberPersistenceException() from e 

        if not m:
            logger.warning("Member not found (mail=%s).", mail)
            raise MemberNotFoundException(message="No account found with this email address.")

        logger.info(
            "Member fetched successfully (id=%s, username=%s, arabic_name=%s, mail=%s).",
            m.id,
            m.username,
            m.arabic_name,
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
            RepoNotFoundException: If the repository is not found.
        """
        logger.info("Fetching members by repository ID (repo_id=%s).", repo_id)

        try:
            repo = self._session.query(GitRepoModel).filter_by(id=repo_id).first()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to fetch members by repository ID (repo_id=%s).", repo_id
            )
            raise MemberPersistenceException() from e 

        if not repo:
            logger.warning("Repository not found when fetching members (repo_id=%s).", repo_id)
            raise RepoNotFoundException(message="Repository not found.")

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
            self._session.rollback()
            logger.exception("Failed to fetch members with repositories.")
            raise MemberPersistenceException() from e 

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
            self._session.rollback()
            logger.exception("Failed to delete member (id=%s).", member_id)
            raise MemberPersistenceException() from e 

        if not m:
            logger.warning("Member not found (id=%s).", member_id)
            raise MemberNotFoundException(message="Member not found.")

        try:
            self._session.delete(m)
            self._session.commit()

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception("Failed to delete member (id=%s).", member_id)
            raise MemberPersistenceException() from e 

        logger.info("Member deleted successfully (id=%s).", m.id)

        return True