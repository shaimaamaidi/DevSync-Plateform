"""
Integration tests for ClickUp space routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup_space import (
    ClickUpRepoDTO,
    ClickUpSpaceCreateDTO,
    ClickUpSpaceDTO,
    ClickUpSpaceDetailDTO,
    ClickUpSpaceLightDTO,
    ClickUpSpaceUpdateDTO,
)


def test_get_all_clickup_spaces(client: TestClient, container) -> None:
    """
    Test getting all ClickUp spaces via the API.
    """
    container.clickup_service.get_all.return_value = [
        ClickUpSpaceDTO(id=1, name="Platform", space_code="PLT")
    ]

    response = client.get("/clickup/")

    assert response.status_code == 200
    assert response.json()[0]["space_code"] == "PLT"
    container.clickup_service.get_all.assert_called_once()


def test_get_all_light_clickup_spaces(client: TestClient, container) -> None:
    """
    Test getting all ClickUp spaces (light) via the API.
    """
    container.clickup_service.get_all_light.return_value = [
        ClickUpSpaceLightDTO(
            id=2,
            name="Ops",
            space_code="OPS",
            repo=ClickUpRepoDTO(id=10, name="repo-one", url="https://example.com/repo"),
        )
    ]

    response = client.get("/clickup/light")

    assert response.status_code == 200
    assert response.json()[0]["space_code"] == "OPS"
    assert response.json()[0]["repo"]["name"] == "repo-one"
    container.clickup_service.get_all_light.assert_called_once()


def test_get_clickup_space_by_id(client: TestClient, container) -> None:
    """
    Test getting a ClickUp space by id via the API.
    """
    container.clickup_service.get_by_id.return_value = ClickUpSpaceDetailDTO(
        id=5,
        name="Platform",
        space_code="PLT",
        repo=ClickUpRepoDTO(id=10, name="repo-one", url="https://example.com/repo"),
    )

    response = client.get("/clickup/5")

    assert response.status_code == 200
    assert response.json()["id"] == 5
    container.clickup_service.get_by_id.assert_called_once_with(5)


def test_create_clickup_space(client: TestClient, container) -> None:
    """
    Test creating a ClickUp space via the API.
    """
    container.clickup_service.add_space.return_value = ClickUpSpaceDTO(
        id=3,
        name="Platform",
        space_code="PLT",
    )

    payload = ClickUpSpaceCreateDTO(name="Platform", space_code="PLT").model_dump()
    response = client.post("/clickup/", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == 3
    container.clickup_service.add_space.assert_called_once()


def test_update_clickup_space(client: TestClient, container) -> None:
    """
    Test updating a ClickUp space via the API.
    """
    container.clickup_service.update_space.return_value = ClickUpSpaceDetailDTO(
        id=7,
        name="Platform",
        space_code="PLT",
        repo=None,
    )

    payload = ClickUpSpaceUpdateDTO(name="Platform", space_code="PLT").model_dump()
    response = client.put("/clickup/7", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == 7
    container.clickup_service.update_space.assert_called_once()
    called_space = container.clickup_service.update_space.call_args[0][0]
    assert called_space.id == 7


def test_delete_clickup_space(client: TestClient, container) -> None:
    """
    Test deleting a ClickUp space via the API.
    """
    container.clickup_service.delete.return_value = True

    response = client.delete("/clickup/7")

    assert response.status_code == 200
    assert response.json() is True
    container.clickup_service.delete.assert_called_once_with(7)
