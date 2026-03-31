"""
Integration tests for repository routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.git_repo import GitRepoDTO
from backend.src.domain.exceptions.repo_not_found_exception import RepoNotFoundException


def test_get_all_repos(client: TestClient, container) -> None:
    """
    Test getting all repositories via the API returns the correct list.
    """
    container.repo_service.get_all.return_value = [
        GitRepoDTO(id=1, name="repo-one", url="https://github.com/org/repo-one")
    ]

    response = client.get("/repo/all")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "repo-one"
    container.repo_service.get_all.assert_called_once()


def test_add_repo(client: TestClient, container) -> None:
    """
    Test adding a repository via the API returns the correct DTO.
    """
    container.repo_service.add_repo.return_value = GitRepoDTO(
        id=2,
        name="repo-two",
        url="https://github.com/org/repo-two",
    )

    response = client.post(
        "/repo/",
        json={"name": "repo-two", "url": "https://github.com/org/repo-two"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 2
    container.repo_service.add_repo.assert_called_once()


def test_get_repo_by_id_returns_not_found(client: TestClient, container) -> None:
    """
    Test getting a repo by ID that does not exist returns a 404 error.
    """
    container.repo_service.get_by_id.side_effect = RepoNotFoundException(
        message="Repository not found with ID: 99"
    )

    response = client.get("/repo/99")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "REPO_NOT_FOUND"
