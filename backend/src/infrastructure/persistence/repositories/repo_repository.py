"""
SQLAlchemy repository for Git repositories.

This module provides a repository implementation for Git repository persistence using SQLAlchemy ORM.
"""

import logging
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoDTO,
    GitRepoDetailDTO,
    GitRepoUpdateDTO,
    RepoClickUpSpaceDTO,
    RepoMemberDTO,
)
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo_persistence_exception import RepoPersistenceException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel


logger = logging.getLogger(__name__)


def _model_to_dto(m: GitRepoModel) -> GitRepoDTO:
    """
    Convert a repository model to a DTO.

    Args:
        m (GitRepoModel): Git repository ORM model.

    Returns:
        GitRepoDTO: Repository DTO.
    """
    return GitRepoDTO(id=m.id, name=m.name, url=m.url)

def _model_to_detail_dto(m: GitRepoModel) -> GitRepoDetailDTO:
    """
    Convert a repository model to a detailed DTO.

    Args:
        m (GitRepoModel): Git repository ORM model.

    Returns:
        GitRepoDetailDTO: Repository detail DTO.
    """
    members = [
        RepoMemberDTO(
    
            id=mb.id,
            username=mb.username,
            mail=mb.mail,
        )
        for mb in m.members
    ]
    space = (
        RepoClickUpSpaceDTO(
            id=m.clickup_space.id,
            name=m.clickup_space.name,
            space_code=m.clickup_space.space_code,
        )
        if m.clickup_space
        else None
    )

    return GitRepoDetailDTO(id=m.id, name=m.name, url=m.url, members=members, clickup_space=space)


class SqlAlchemyRepoRepository(IRepoRepository):
    """
    SQLAlchemy implementation of IRepoRepository for Git repository persistence.

    This repository handles CRUD operations for Git repositories using SQLAlchemy ORM.

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

    def save(self, repo: GitRepoCreateDTO) -> GitRepoDTO:
        """
        Create a repository record.

        Args:
            repo (GitRepoCreateDTO): Repository create DTO.

        Returns:
            GitRepoDTO: Created repository DTO.

        Raises:
            InvalidInputException: If required arguments are missing or repository already exists.
            RepoPersistenceException: For database errors during persistence.
        """
        logger.info(
            "Creating new repository (name=%s, url=%s).",
        
            repo.name,
            repo.url
        )

        if not repo.name or not repo.url:
            logger.warning(
                "Invalid input for repository creation (name=%s, url=%s).",
                repo.name,
                repo.url
            )
            raise InvalidInputException(
                "GitHub Repo must have a valid 'name' and 'url' for create."
            )

        try:
            m = GitRepoModel(name=repo.name, url=repo.url)
            self._session.add(m)
            self._session.commit()
            self._session.refresh(m)

            logger.info(
                "Repository created successfully (id=%s, url=%s).",
                m.id,
                m.url
            )

            return _model_to_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Repository already exists (url=%s) in another resource.", repo.url)
            raise InvalidInputException("Repository with this URL already exists in another resource.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to create repository (url=%s).",
                repo.url
            )
            raise RepoPersistenceException(str(e)) from e

    def update(self, repo: GitRepoUpdateDTO) -> GitRepoDetailDTO:
        """
        Update a repository record.

        Args:
            repo (GitRepoUpdateDTO): Repository update DTO.

        Returns:
            GitRepoDetailDTO: Updated repository detail DTO.

        Raises:
            InvalidInputException: If required arguments are missing or invalid association.
            RepoNotFoundException: If the repository is not found.
            RepoPersistenceException: For database errors during update.
        """
        logger.info("Updating repository (id=%s).", repo.id)

        if not repo.id:
            logger.warning("Update failed: missing repository ID.")
            raise InvalidInputException("GitHub Repo must have a valid database ID for update.")

        if (
            not repo.name
            and not repo.url
            and (repo.members is None or not repo.members)
            and repo.clickup_space is None
        ):
            logger.warning("Update failed: no fields provided (id=%s).", repo.id)
            raise InvalidInputException(
                "GitHub Repo must have at least one field to update: 'name', 'url', 'members' or 'clickup_space'."
            )

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo.id).first()

        except SQLAlchemyError as e:
            logger.exception(
                "Failed to update repository (id=%s).",
                repo.id
            )
            raise RepoPersistenceException(str(e)) from e
    
        if not m:
            logger.warning("Repository not found for update (id=%s).", repo.id)
            raise RepoNotFoundException(message=f"Repository not found with ID : {repo.id}")

        if repo.name:
            m.name = repo.name
    
        if repo.url:
            m.url = repo.url

        if repo.members is not None:
            deduped_members = {}
            if not repo.members:
                logger.info("Members list is empty (repo_id=%s).",repo.id,)
            else:
                if not any(m.id or m.mail for m in repo.members):
                    raise InvalidInputException(
                        "Members must include at least one 'id' or 'mail'."
                    )

                existing_members = []
                missing_ids = set()
                missing_mails = set()
                
                for member in repo.members:
                    if member.id:
                        mem = (
                            self._session.query(MemberModel)
                            .filter(MemberModel.id == member.id)
                            .first()
                        )
                        if mem:
                            existing_members.append(mem)
                            continue
                        if member.mail:
                            mem = (
                                self._session.query(MemberModel)
                                .filter(MemberModel.mail == member.mail)
                                .first()
                            )
                            if mem:
                                existing_members.append(mem)
                            else:
                                missing_ids.add(member.id)
                                missing_mails.add(member.mail)
                        else:
                            missing_ids.add(member.id)
                    elif member.mail:
                        mem = (
                            self._session.query(MemberModel)
                            .filter(MemberModel.mail == member.mail)
                            .first()
                        )
                        if mem:
                            existing_members.append(mem)
                        else:
                            missing_mails.add(member.mail)

                deduped_members = {mem.id: mem for mem in existing_members}.values()
                
                if missing_ids or missing_mails:
                    missing_info = []
                    if missing_ids:
                        missing_info.append(f"ids={missing_ids}")
                    if missing_mails:
                        missing_info.append(f"mails={missing_mails}")
                    raise InvalidInputException(
                        "Members not found for update (%s)." % ", ".join(missing_info)
                    )

            m.members = list(deduped_members)
            logger.info(
                "Members association updated for repository (id=%s, count=%s).",
                repo.id,
                len(m.members)
            )

        if repo.clickup_space is not None:
            if not repo.clickup_space.id and not repo.clickup_space.space_code:
                raise InvalidInputException(
                    "ClickUp space must include 'id' or 'space_code' for association."
                )

            clickup_space_model = None

            if repo.clickup_space.id:
                clickup_space_model = (
                    self._session.query(ClickUpSpaceModel)
                    .filter(ClickUpSpaceModel.id == repo.clickup_space.id)
                    .first()
                )

            if not clickup_space_model and repo.clickup_space.space_code:
                clickup_space_model = (
                    self._session.query(ClickUpSpaceModel)
                    .filter(
                        ClickUpSpaceModel.space_code == repo.clickup_space.space_code,
                        ClickUpSpaceModel.space_code.isnot(None)
                    )
                    .first()
                )

            if clickup_space_model:
                if clickup_space_model.repo_id and clickup_space_model.repo_id != m.id:
                    raise InvalidInputException(
                        "ClickUp space is already associated with another repository."
                    )
                m.clickup_space = clickup_space_model
                logger.info(
                    "ClickUp space associated with repository (id=%s).",
                    repo.id,
                )
            else:
                raise InvalidInputException(
                    "ClickUp space not found for association (id=%s, space_code=%s)."
                    % (repo.clickup_space.id, repo.clickup_space.space_code)
                )
            
        try:
            self._session.commit()
            self._session.refresh(m)

            logger.info("Repository updated successfully (id=%s).", m.id)

            return _model_to_detail_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Repository already exists (url=%s) in another resource.", repo.url)
            raise InvalidInputException("Repository with this URL already exists in another resource.") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to update repository (id=%s).",
                repo.id
            )
            raise RepoPersistenceException(str(e)) from e

    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        """
        Fetch a repository by id.

        Args:
            repo_id (int): Repository id.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.

        Raises:
            RepoNotFoundException: If the repository is not found.
            RepoPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching repository (id=%s).", repo_id)

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
            
        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching repository (id=%s).",
                repo_id,
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s).", repo_id)
            raise RepoNotFoundException(message=f"Repository not found with ID: {repo_id}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s).",
            m.id,
            m.name,
            m.url
        )

        return _model_to_detail_dto(m)

    def find_by_url(self, url: str) -> GitRepoDTO:
        """
        Fetch a repository by URL.

        Args:
            url (str): Repository URL.

        Returns:
            GitRepoDTO: Repository DTO.

        Raises:
            RepoNotFoundException: If the repository is not found.
            RepoPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching repository by url (url=%s).", url)

        try:
            m = self._session.query(GitRepoModel).filter_by(url=url).first()
            
        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching repository by url (url=%s).",
                url
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (url=%s).", url)
            raise RepoNotFoundException(message=f"Repository not found with URL: {url}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s).",
            m.id,
            m.name,
            m.url
        )

        return _model_to_dto(m)

    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        """
        Fetch a repository by name.

        Args:
            name (str): Repository name.

        Returns:
            GitRepoDetailDTO: Repository detail DTO.

        Raises:
            RepoNotFoundException: If the repository is not found.
            RepoPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching repository by name (name=%s).", name)

        try:
            m = self._session.query(GitRepoModel).filter_by(name=name).first()
            
        except SQLAlchemyError as e:
            logger.exception(
                "Error Fetching repository by name (name=%s).",
                name,
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (name=%s).", name)
            raise RepoNotFoundException(message=f"Repository not found with NAME: {name}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s).",
            m.id,
            m.name,
            m.url
        )

        return _model_to_detail_dto(m)

    def find_all(self) -> List[GitRepoDTO]:
        """
        Fetch all repositories.

        Returns:
            List[GitRepoDTO]: List of repository DTOs.

        Raises:
            RepoPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching all repositories.")

        try:
            results = [_model_to_dto(m) for m in self._session.query(GitRepoModel).all()]

        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching all repositories."
            )
            raise RepoPersistenceException(str(e)) from e
            
        logger.info(
            "Fetched all repositories successfully (count=%s).",
            len(results),
        )

        return results

    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        """
        Fetch all repositories with details.

        Returns:
            List[GitRepoDetailDTO]: List of repository detail DTOs.

        Raises:
            RepoPersistenceException: For database errors during fetch.
        """
        logger.info("Fetching all repositories with details.")
        
        try:
            results = [_model_to_detail_dto(m) for m in self._session.query(GitRepoModel).all()]

        except SQLAlchemyError as e:
            logger.exception(
                "Error fetching all repositories with details."
            )
            raise RepoPersistenceException(str(e)) from e
            
        logger.info(
            "Fetched all repositories successfully (count=%s).",
            len(results),
        )

        return results

    def delete(self, repo_id: int) -> bool:
        """
        Delete a repository by id.

        Args:
            repo_id (int): Repository id.

        Returns:
            bool: True when deletion succeeds.

        Raises:
            RepoNotFoundException: If the repository is not found.
            RepoPersistenceException: For database errors during deletion.
        """
        logger.info("Deleting repository (id=%s).", repo_id)
        
        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
            
        except SQLAlchemyError as e:
            logger.exception(
                "Error deleting repository (id=%s).",
                repo_id
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s).", repo_id)
            raise RepoNotFoundException(message=f"Repository not found with ID: {repo_id}")

        try:
            self._session.delete(m)
            self._session.commit()

            logger.info("Repository deleted successfully (id=%s).", m.id)

            return True

        except SQLAlchemyError as e:
            self._session.rollback()
            logger.exception(
                "Failed to delete repository (id=%s).",
                repo_id
            )
            raise RepoPersistenceException(str(e)) from e