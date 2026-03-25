import logging
from typing import List

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, MemberSummary, ClickUpSpaceSummary
from backend.src.domain.entities.member import RepoSummary
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo_persistence_exception import RepoPersistenceException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel


logger = logging.getLogger(__name__)


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
        logger.info(
            "Creating new repository (name=%s, url=%s)",
            repo.name,
            repo.url
        )

        if not repo.name or not repo.url:
            logger.warning(
                "Invalid input for repository creation (name=%s, url=%s)",
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
                "Repository created successfully (id=%s, url=%s)",
                m.id,
                m.url
            )

            return _model_to_dto(m)

        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to create repository (url=%s): %s",
                repo.url,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

    def update(self, repo: GitRepoDTO) -> GitRepoDTO:
        logger.info("Updating repository (id=%s)", repo.id)

        if not repo.id:
            logger.warning("Update failed: missing repository ID")
            raise InvalidInputException("GitHub Repo must have a valid database ID for update.")

        if not repo.name and not repo.url:
            logger.warning("Update failed: no fileds provided (id=%s)", repo.id)
            raise InvalidInputException(
                "GitHub Repo must have a valid 'name' or 'url' for update."
            )

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo.id).first()

            if not m:
                logger.warning("Repository not found for update (id=%s)", repo.id)
                raise RepoNotFoundException(repo.id)

            if repo.name:
                m.name = repo.name
            if repo.url:
                m.url = repo.url

            self._session.commit()
            self._session.refresh(m)

            logger.info("Repository updated successfully (id=%s)", m.id)

            return _model_to_dto(m)

        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to update repository (id=%s): %s",
                repo.id,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

    def find_by_id(self, repo_id: int) -> GitRepoDTO:
        logger.info("Fetching repository (id=%s)", repo_id)

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        except Exception as e:
            logger.error(
                "Error fetching repository (id=%s): %s",
                repo_id,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s)", repo_id)
            raise RepoNotFoundException(repo_id)

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_dto(m)

    def find_by_url(self, url: str) -> GitRepoDTO:
        logger.info("Fetching repository by url (url=%s)", url)

        try:
            m = self._session.query(GitRepoModel).filter_by(url=url).first()
        except Exception as e:
            logger.error(
                "Error fetching repository by url (url=%s): %s",
                url,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (url=%s)", url)
            raise RepoNotFoundException(url)

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_dto(m)

    def find_by_name(self, name: str) -> GitRepoDTO:
        logger.info("Fetching repository by name (name=%s)", name)

        try:
            m = self._session.query(GitRepoModel).filter_by(name=name).first()
        except Exception as e:
            logger.error(
                "Error Fetching repository by name (name=%s): %s",
                name,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (name=%s)", name)
            raise RepoNotFoundException(name)

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_dto(m)

    def find_all(self) -> List[GitRepoDTO]:
        logger.info("Fetching all repositories")

        try:
            results = [_model_to_dto(m) for m in self._session.query(GitRepoModel).all()]

            logger.info(
                "Fetched all repositories successfully (count=%s)",
                len(results),
            )

            return results

        except Exception as e:
            logger.error(
                "Error fetching all repositories: %s",
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

    def find_all_with_details(self) -> List[GitRepoDetailDTO]:
        logger.info("Fetching all repositories with details")

        try:
            results = [_model_to_detail_dto(m) for m in self._session.query(GitRepoModel).all()]

            logger.info(
                "Fetched all repositories successfully (count=%s)",
                len(results),
            )

            return results

        except Exception as e:
            logger.error(
                "Error fetching all repositories with details: %s",
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

    def delete(self, repo_id: int) -> bool:
        logger.info("Deleting repository (id=%s)", repo_id)

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        except Exception as e:
            logger.error(
                "Error deleting repository (id=%s): %s",
                repo_id,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s)", repo_id)
            raise RepoNotFoundException(repo_id)

        try:
            self._session.delete(m)
            self._session.commit()

            logger.info("Repository deleted successfully (id=%s)", m.id)

            return True

        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to delete repository (id=%s): %s",
                repo_id,
                str(e),
                exc_info=e
            )
            raise RepoPersistenceException(str(e)) from e