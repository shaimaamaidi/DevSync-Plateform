"""Integration tests for associator routes."""

from fastapi.testclient import TestClient
from backend.src.domain.entities.associator import AssociateClickUpSpaceResponse, AssociateMembersResponse


def test_associate_space_success(client: TestClient, container) -> None:
    container.associator_service.associate_clickup_space.return_value = AssociateClickUpSpaceResponse(
        repo_url="https://github.com/org/repo", space_code="PLT"
    )
    response = client.post("/associator/space", json={"repo_url": "https://github.com/org/repo", "space_code": "PLT"})
    assert response.status_code == 200
    assert response.json()["space_code"] == "PLT"
    container.associator_service.associate_clickup_space.assert_called_once()


def test_add_members_success(client: TestClient, container) -> None:
    container.associator_service.add_members.return_value = AssociateMembersResponse(repo_url="https://github.com/org/repo", members=[])
    response = client.post("/associator/members/add", json={"repo_url": "https://github.com/org/repo", "members": []})
    assert response.status_code == 200
    assert response.json()["repo_url"] == "https://github.com/org/repo"
    container.associator_service.add_members.assert_called_once()
