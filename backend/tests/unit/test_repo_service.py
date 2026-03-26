"""Unit tests for RepoService."""

from unittest.mock import MagicMock

from backend.src.application.services.repo_service import RepoService
from backend.src.domain.entities.git_repo import GitRepoCreateDTO, GitRepoDTO, GitRepoIdDTO


def test_add_repo_calls_repository_save() -> None:
    repo_repo = MagicMock()
    repo_repo.save.return_value = GitRepoDTO(id=1, name="repo", url="https://example.com/repo")
    service = RepoService(repo_repo)

    result = service.add_repo(GitRepoCreateDTO(name="repo", url="https://example.com/repo"))

    repo_repo.save.assert_called_once()
    assert result.id == 1


def test_delete_repo_calls_repository_delete() -> None:
    repo_repo = MagicMock()
    repo_repo.delete.return_value = True
    service = RepoService(repo_repo)

    result = service.delete(GitRepoIdDTO(id=12))

    repo_repo.delete.assert_called_once_with(12)
    assert result is True
