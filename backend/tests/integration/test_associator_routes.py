"""
Integration tests for associator routes.
"""

from fastapi.testclient import TestClient
from backend.src.domain.entities.associator import AssociatorRepoDTO, AssociateClickUpSpaceResponse, AssociateMembersResponse


def test_associate_space_success(client: TestClient, container) -> None:
    """
    Test associating a ClickUp space via the API returns the correct repo DTO.
    """
    container.associator_use_case.associate_clickup_space.return_value = AssociateClickUpSpaceResponse(
        repo=AssociatorRepoDTO(id=1, name="repo", url="https://github.com/org/repo"),
        clickup_space=None
    )
    response = client.post("/associate/space", json={"repo_url": "https://github.com/org/repo", "space_code": "PLT"})
    assert response.status_code == 200
    data = response.json()
    assert data["repo"]["url"] == "https://github.com/org/repo"
    assert data["repo"]["id"] == 1
    container.associator_use_case.associate_clickup_space.assert_called_once()


def test_add_members_success(client: TestClient, container) -> None:
    """
    Test adding members via the API returns the correct repo DTO.
    """
    container.associator_use_case.add_members.return_value = AssociateMembersResponse(
        repo=AssociatorRepoDTO(id=1, name="repo", url="https://github.com/org/repo")
    )
    response = client.post("/associate/members/add", json={"repo_url": "https://github.com/org/repo", "members": []})
    assert response.status_code == 200
    data = response.json()
    assert data["repo"]["url"] == "https://github.com/org/repo"
    assert data["repo"]["id"] == 1
    container.associator_use_case.add_members.assert_called_once()
