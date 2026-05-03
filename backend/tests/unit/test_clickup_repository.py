"""
Unit tests for SqlAlchemyClickUpRepository.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.src.domain.entities.clickup_space import (
    ClickUpRepoRefDTO,
    ClickUpSpaceCreateDTO,
    ClickUpSpaceUpdateDTO,
)
from backend.src.domain.exceptions.clickup.clickup_persistence_exception import ClickUpPersistenceException
from backend.src.domain.exceptions.clickup.clickup_space_not_found_exception import ClickUpSpaceNotFoundException
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.infrastructure.persistence.repositories.clickup_repository import SqlAlchemyClickUpRepository


def test_clickup_save_requires_fields() -> None:
    """
    save should raise InvalidInputException when fields missing.
    """
    repo = SqlAlchemyClickUpRepository(MagicMock())

    with pytest.raises(InvalidInputException):
        repo.save(ClickUpSpaceCreateDTO(name=None, space_code=None))


def test_clickup_update_requires_id() -> None:
    """
    update should raise InvalidInputException when id missing.
    """
    repo = SqlAlchemyClickUpRepository(MagicMock())

    with pytest.raises(InvalidInputException):
        repo.update(ClickUpSpaceUpdateDTO(id=None, name="n"))


def test_clickup_find_by_id_not_found() -> None:
    """
    find_by_id should raise ClickUpSpaceNotFoundException when no record.
    """
    session = MagicMock()
    session.query.return_value.options.return_value.filter_by.return_value.first.return_value = None
    repo = SqlAlchemyClickUpRepository(session)

    with pytest.raises(ClickUpSpaceNotFoundException):
        repo.find_by_id(55)


def test_clickup_find_all_light_wraps_sqlalchemy_error() -> None:
    """
    find_all_light should wrap SQLAlchemyError into ClickUpPersistenceException.
    """
    session = MagicMock()
    session.query.return_value.options.return_value.all.side_effect = SQLAlchemyError("fail")
    repo = SqlAlchemyClickUpRepository(session)

    with pytest.raises(ClickUpPersistenceException):
        repo.find_all_light()


def test_clickup_update_happy_path() -> None:
    """
    update should commit and return detail DTO.
    """
    model = SimpleNamespace(id=1, name="old", space_code="PLT", repo=None)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model
    session.query.return_value.options.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyClickUpRepository(session)
    result = repo.update(ClickUpSpaceUpdateDTO(id=1, name="new"))

    assert result.id == 1
    assert result.name == "new"
    session.commit.assert_called_once()


def test_clickup_delete_happy_path() -> None:
    """
    delete should remove record and commit.
    """
    model = SimpleNamespace(id=4)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyClickUpRepository(session)
    result = repo.delete(4)

    assert result is True
    session.delete.assert_called_once_with(model)
    session.commit.assert_called_once()


def test_clickup_update_repo_by_id() -> None:
    """
    update should associate repo by id.
    """
    repo_model = SimpleNamespace(
        id=9,
        name="repo",
        url="https://example.com/repo",
        clickup_space=None
    )

    space_model = SimpleNamespace(
        id=1,
        name="Space",
        space_code="SPC",
        repo=None
    )

    session = MagicMock()

    query_mock = MagicMock()

    query_mock.filter_by.return_value.first.return_value = space_model
    query_mock.options.return_value.filter_by.return_value.first.return_value = space_model

    query_mock.filter.return_value.first.return_value = repo_model

    session.query.return_value = query_mock

    repo = SqlAlchemyClickUpRepository(session)

    result = repo.update(
        ClickUpSpaceUpdateDTO(
            id=1,
            repo=ClickUpRepoRefDTO(id=9)
        )
    )

    assert result.id == 1
    assert space_model.repo.id == 9
    session.commit.assert_called_once()


def test_clickup_update_repo_by_url() -> None:
    """
    update should associate repo by url.
    """
    repo_model = MagicMock()
    repo_model.id = 9
    repo_model.name = "my-repo"
    repo_model.url = "https://example.com/repo"
    repo_model.clickup_space = None

    space_model = MagicMock()
    space_model.id = 1
    space_model.name = "my-space"
    space_model.space_code = "SPC"
    space_model.repo = None

    session = MagicMock()

    space_query = MagicMock()
    space_query.filter_by.return_value.first.return_value = space_model
    space_query.options.return_value.filter_by.return_value.first.return_value = space_model

    repo_query = MagicMock()
    repo_query.filter.return_value.first.return_value = repo_model

    def query_side_effect(model):
        if model.__name__ == "ClickUpSpaceModel":
            return space_query

        elif model.__name__ == "GitRepoModel":
            return repo_query

        return MagicMock()

    session.query.side_effect = query_side_effect

    repo = SqlAlchemyClickUpRepository(session)

    result = repo.update(
        ClickUpSpaceUpdateDTO(
            id=1,
            repo=ClickUpRepoRefDTO(url="https://example.com/repo")
        )
    )

    assert result is not None
    assert space_model.repo == repo_model


def test_clickup_update_repo_missing_raises() -> None:
    """
    update should raise InvalidInputException when repo does not exist.
    """
    space_model = SimpleNamespace(id=1, name="Space", space_code="SPC", repo=None)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = space_model

    repo = SqlAlchemyClickUpRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(ClickUpSpaceUpdateDTO(id=1, repo=ClickUpRepoRefDTO(id=99)))


def test_clickup_update_repo_requires_id_or_url() -> None:
    """
    update should raise InvalidInputException when repo ref lacks id/url.
    """
    space_model = SimpleNamespace(id=1, name="Space", space_code="SPC", repo=None)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = space_model

    repo = SqlAlchemyClickUpRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(ClickUpSpaceUpdateDTO(id=1, repo=ClickUpRepoRefDTO()))


def test_clickup_update_repo_already_associated_raises() -> None:
    """
    update should raise InvalidInputException when repo already linked to another ClickUp space.
    """
    other_space = SimpleNamespace(id=2)
    repo_model = SimpleNamespace(
        id=9,
        name="repo",
        url="https://example.com/repo",
        clickup_space=other_space,
    )
    space_model = SimpleNamespace(id=1, name="Space", space_code="SPC", repo=None)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = space_model
    session.query.return_value.options.return_value.filter_by.return_value.first.return_value = repo_model

    repo = SqlAlchemyClickUpRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(ClickUpSpaceUpdateDTO(id=1, repo=ClickUpRepoRefDTO(id=9)))
