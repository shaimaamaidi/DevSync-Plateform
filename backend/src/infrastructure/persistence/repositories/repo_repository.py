import logging
from typing import List

from sqlalchemy.exc import IntegrityError

from backend.src.domain.entities.git_repo import GitRepoDTO, GitRepoDetailDTO, MemberSummary, ClickUpSpaceSummary
from backend.src.domain.entities.member import RepoSummary
from backend.src.domain.exceptions.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo_persistence_exception import RepoPersistenceException
from backend.src.domain.ports.repositories.i_repo_repository import IRepoRepository
from backend.src.infrastructure.persistence.models.clickup_space_model import ClickUpSpaceModel
from backend.src.infrastructure.persistence.models.git_repo_model import GitRepoModel
from backend.src.infrastructure.persistence.models.member_model import MemberModel

logger = logging.getLogger(__name__)


def _model_to_dto(m: GitRepoModel) -> GitRepoDTO:
    return GitRepoDTO(id=m.id, name=m.name, url=m.url)


def _model_to_detail_dto(m: GitRepoModel) -> GitRepoDetailDTO:
    members = [
        MemberSummary(
            username=mb.username,
            mail=mb.mail,
            repos=[RepoSummary(name=r.name, url=r.url) for r in mb.repos]
        )
        for mb in m.members
    ]
    space = (
        ClickUpSpaceSummary(name=m.clickup_space.name, space_code=m.clickup_space.space_id)
        if m.clickup_space
        else None
    )
    return GitRepoDetailDTO(id=m.id, name=m.name, url=m.url, members=members, clickup_space=space)

class SqlAlchemyRepoRepository(IRepoRepository):
    def __init__(self, session):
        self._session = session

    def save(self, repo: GitRepoDTO) -> GitRepoDetailDTO:
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

            return _model_to_detail_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Repository already exists (url=%s)", repo.url)
            raise InvalidInputException("Repository with this URL already exists.") from e
        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to create repository (url=%s): %s",
                repo.url,
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

    def update(self, repo: GitRepoDetailDTO) -> GitRepoDetailDTO:
        logger.info("Updating repository (id=%s)", repo.id)

        if not repo.id:
            logger.warning("Update failed: missing repository ID")
            raise InvalidInputException("GitHub Repo must have a valid database ID for update.")

        if not repo.name and not repo.url and repo.members is None and repo.clickup_space is None:
            logger.warning("Update failed: no fields provided (id=%s)", repo.id)
            raise InvalidInputException(
                "GitHub Repo must have at least one field to update: 'name', 'url', 'members' or 'clickup_space'."
            )

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo.id).first()

            if not m:
                logger.warning("Repository not found for update (id=%s)", repo.id)
                raise RepoNotFoundException(message=f"Repository not found with ID : {repo.id}")

            if repo.name:
                m.name = repo.name
            if repo.url:
                m.url = repo.url

            if repo.members is not None:
                incoming_mails = {member.mail for member in repo.members}

                existing_members = (
                    self._session.query(MemberModel)
                    .filter(MemberModel.mail.in_(incoming_mails))
                    .all()
                )

                found_mails = {mem.mail for mem in existing_members}
                missing_mails = incoming_mails - found_mails

                if missing_mails:
                    logger.warning(
                        "Some members not found and will be skipped (mails=%s)",
                        missing_mails
                    )

                m.members = existing_members
                logger.info(
                    "Members association updated for repository (id=%s, count=%s)",
                    repo.id,
                    len(existing_members)
                )

            if repo.clickup_space is not None and repo.clickup_space.space_code:
                clickup_space_model = (
                    self._session.query(ClickUpSpaceModel)
                    .filter(
                        ClickUpSpaceModel.space_code == repo.clickup_space.space_code,
                        ClickUpSpaceModel.space_code.isnot(None)
                    )
                    .first()
                )

                if clickup_space_model:
                    m.clickup_space = clickup_space_model
                    logger.info(
                        "ClickUp space associated with repository (id=%s, space_code=%s)",
                        repo.id,
                        repo.clickup_space.space_code
                    )
                else:
                    logger.warning(
                        "ClickUp space not found or space_code is null in DB (space_code=%s), skipping association",
                        repo.clickup_space.space_code
                    )

            self._session.commit()
            self._session.refresh(m)

            logger.info("Repository updated successfully (id=%s)", m.id)

            return _model_to_detail_dto(m)

        except IntegrityError as e:
            self._session.rollback()
            logger.warning("Repository already exists (url=%s)", repo.url)
            raise InvalidInputException("Repository with this URL already exists.") from e
        except RepoPersistenceException:
            raise
        except Exception as e:
            self._session.rollback()
            logger.error(
                "Failed to update repository (id=%s): %s",
                repo.id,
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

    def find_by_id(self, repo_id: int) -> GitRepoDetailDTO:
        logger.info("Fetching repository (id=%s)", repo_id)

        try:
            m = self._session.query(GitRepoModel).filter_by(id=repo_id).first()
        except Exception as e:
            logger.error(
                "Error fetching repository (id=%s): %s",
                repo_id,
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s)", repo_id)
            raise RepoNotFoundException(message=f"Repository not found with ID: {repo_id}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_detail_dto(m)

    def find_by_url(self, url: str) -> GitRepoDetailDTO:
        logger.info("Fetching repository by url (url=%s)", url)

        try:
            m = self._session.query(GitRepoModel).filter_by(url=url).first()
        except Exception as e:
            logger.error(
                "Error fetching repository by url (url=%s): %s",
                url,
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (url=%s)", url)
            raise RepoNotFoundException(message=f"Repository not found with URL: {url}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_detail_dto(m)

    def find_by_name(self, name: str) -> GitRepoDetailDTO:
        logger.info("Fetching repository by name (name=%s)", name)

        try:
            m = self._session.query(GitRepoModel).filter_by(name=name).first()
        except Exception as e:
            logger.error(
                "Error Fetching repository by name (name=%s): %s",
                name,
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (name=%s)", name)
            raise RepoNotFoundException(message=f"Repository not found with NAME: {name}")

        logger.info(
            "Repository fetched successfully (id=%s, name=%s, url=%s)",
            m.id,
            m.name,
            m.url
        )

        return _model_to_detail_dto(m)

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
                str(e)
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
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e

        if not m:
            logger.warning("Repository not found (id=%s)", repo_id)
            raise RepoNotFoundException(message=f"Repository not found with ID: {repo_id}")

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
                str(e)
            )
            raise RepoPersistenceException(str(e)) from e