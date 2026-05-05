"""
Integration tests for ClickUp structure routes.
"""

from fastapi.testclient import TestClient

from backend.src.domain.entities.clickup.folder_with_list_metadata import FolderWithListsMetadata
from backend.src.domain.entities.clickup.list_metadata import ClickUpListMetadata
from backend.src.domain.entities.clickup.status import StatusType
from backend.src.domain.entities.clickup_space import ClickUpSpaceDTO


def test_create_clickup_space_structure(client: TestClient, container) -> None:
    container.clickup_structure_creation_use_case.create_space.return_value = ClickUpSpaceDTO(
        id=1,
        name="Platform",
        space_code="PLT",
    )

    response = client.post("/clickup/structure/spaces", json={"space_id": "space-1"})

    assert response.status_code == 201
    assert response.json()["space_code"] == "PLT"
    container.clickup_structure_creation_use_case.create_space.assert_called_once()


def test_create_clickup_folder_structure(client: TestClient, container) -> None:
    container.clickup_structure_creation_use_case.create_folder.return_value = FolderWithListsMetadata(
        id="folder-1",
        name="Backend",
        lists=[],
    )

    response = client.post("/clickup/structure/folders", json={"space_id": "space-1", "name": "Backend"})

    assert response.status_code == 201
    assert response.json()["id"] == "folder-1"
    assert response.json()["lists"] == []
    container.clickup_structure_creation_use_case.create_folder.assert_called_once()


def test_create_clickup_list_structure(client: TestClient, container) -> None:
    container.clickup_structure_creation_use_case.create_list.return_value = ClickUpListMetadata(
        id="list-1",
        name="Sprint",
        statuses=["To Do"],
        priorities=["High"],
    )

    response = client.post(
        "/clickup/structure/lists",
        json={"space_id": "space-1", "name": "Sprint", "folder_id": "folder-1"},
    )

    assert response.status_code == 201
    assert response.json()["id"] == "list-1"
    assert response.json()["statuses"] == ["To Do"]
    container.clickup_structure_creation_use_case.create_list.assert_called_once()


def test_add_clickup_list_status_structure(client: TestClient, container) -> None:
    container.clickup_structure_creation_use_case.add_status.return_value = ClickUpListMetadata(
        id="list-1",
        name="Sprint",
        statuses=["Review"],
        priorities=[],
    )

    response = client.post(
        "/clickup/structure/lists/list-1/statuses",
        json={"list_id": "ignored", "status": "Review", "color": "#ff0000", "type": StatusType.CUSTOM.value},
    )

    assert response.status_code == 201
    assert response.json()["statuses"] == ["Review"]
    called_request = container.clickup_structure_creation_use_case.add_status.call_args.args[0]
    assert called_request.list_id == "list-1"
    assert called_request.status == "Review"


def test_get_clickup_structure_metadata(client: TestClient, container) -> None:
    container.clickup_structure_metadata_use_case.get_space_structure_metadata.return_value = [
        FolderWithListsMetadata(
            id="folder-1",
            name="Backend",
            lists=[ClickUpListMetadata(id="list-1", name="Sprint", statuses=["To Do"], priorities=[])],
        )
    ]

    response = client.get("/clickup/structure/spaces/space-1/metadata")

    assert response.status_code == 200
    assert response.json()[0]["id"] == "folder-1"
    assert response.json()[0]["lists"][0]["name"] == "Sprint"
    container.clickup_structure_metadata_use_case.get_space_structure_metadata.assert_called_once_with("space-1")