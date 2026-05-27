"""
Unit tests for RepoService.
"""

from unittest.mock import MagicMock

from backend.src.application.services.repo_service import RepoService
from backend.src.domain.entities.git_repo import GitRepoCreateDTO, GitRepoDTO


def test_add_repo_calls_repository_save() -> None:
    """
    Test that adding a repo calls the repository's save method and returns the correct DTO.
    """
    repo_repo = MagicMock()
    repo_repo.save.return_value = GitRepoDTO(id=1, name="repo", url="https://example.com/repo")
    service = RepoService(repo_repo)

    result = service.add_repo(GitRepoCreateDTO(name="repo", url="https://example.com/repo"))

    repo_repo.save.assert_called_once()
    assert result.id == 1


def test_delete_repo_calls_repository_delete() -> None:
    """
    Test that deleting a repo calls the repository's delete method and returns True.
    """
    repo_repo = MagicMock()
    repo_repo.delete.return_value = True
    service = RepoService(repo_repo)

    result = service.delete(repo_id=12)

    repo_repo.delete.assert_called_once_with(12)
    assert result is True
