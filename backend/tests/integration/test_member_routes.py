"""
Integration tests for member routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.member import MemberDTO, MemberWithReposDTO


def test_get_all_with_repos(client: TestClient, container) -> None:
    """
    Test getting all members with their repos via the API returns the correct list.
    """
    container.member_service.get_all_with_repos.return_value = [
        MemberWithReposDTO(id=1, username="alice", mail="a@b.com", repos=[])
    ]

    response = client.get("/member/all-with-repos")

    assert response.status_code == 200
    assert response.json()[0]["username"] == "alice"
    container.member_service.get_all_with_repos.assert_called_once()


def test_add_member(client: TestClient, container) -> None:
    """
    Test adding a member via the API returns the correct DTO.
    """
    container.member_service.add_member.return_value = MemberDTO(id=2, username="bob", mail="b@c.com")

    response = client.post("/member/", json={"username": "bob", "mail": "b@c.com"})

    assert response.status_code == 200
    assert response.json()["id"] == 2
    container.member_service.add_member.assert_called_once()
