"""
Unit tests for SqlAlchemyRepoRepository.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.src.domain.entities.git_repo import (
    GitRepoCreateDTO,
    GitRepoUpdateDTO,
    RepoClickUpSpaceRefDTO,
    RepoMemberRefDTO,
)
from backend.src.domain.exceptions.common.invalid_input_exception import InvalidInputException
from backend.src.domain.exceptions.repo.repo_not_found_exception import RepoNotFoundException
from backend.src.domain.exceptions.repo.repo_persistence_exception import RepoPersistenceException
from backend.src.infrastructure.persistence.repositories.repo_repository import SqlAlchemyRepoRepository


def test_repo_save_requires_name_and_url() -> None:
    """
    save should raise InvalidInputException when name/url missing.
    """
    repo = SqlAlchemyRepoRepository(MagicMock())

    with pytest.raises(InvalidInputException):
        repo.save(GitRepoCreateDTO(name=None, url=None))


def test_repo_find_by_id_not_found() -> None:
    """
    find_by_id should raise RepoNotFoundException when no record.
    """
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(RepoNotFoundException):
        repo.find_by_id(99)


def test_repo_find_all_wraps_sqlalchemy_error() -> None:
    """
    find_all should wrap SQLAlchemyError into RepoPersistenceException.
    """
    session = MagicMock()
    session.query.return_value.all.side_effect = SQLAlchemyError("fail")
    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(RepoPersistenceException):
        repo.find_all()


def test_repo_delete_not_found() -> None:
    """
    delete should raise RepoNotFoundException when no record.
    """
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(RepoNotFoundException):
        repo.delete(42)


def test_repo_update_happy_path() -> None:
    """
    update should commit and return detail DTO.
    """
    model = SimpleNamespace(
        id=1,
        name="old",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyRepoRepository(session)
    result = repo.update(GitRepoUpdateDTO(id=1, name="new"))

    assert result.id == 1
    assert result.name == "new"
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(model)


def test_repo_delete_happy_path() -> None:
    """
    delete should remove record and commit.
    """
    model = SimpleNamespace(id=2)
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = model

    repo = SqlAlchemyRepoRepository(session)
    result = repo.delete(2)

    assert result is True
    session.delete.assert_called_once_with(model)
    session.commit.assert_called_once()


def test_repo_update_members_association_by_id() -> None:
    """
    update should associate members when ids exist.
    """
    member_model = SimpleNamespace(id=10, username="alice", mail="a@b.com")
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        member_model,
    ]

    repo = SqlAlchemyRepoRepository(session)
    result = repo.update(
        GitRepoUpdateDTO(id=1, members=[RepoMemberRefDTO(id=10)])
    )

    assert result.id == 1
    assert repo_model.members[0].id == 10
    session.commit.assert_called_once()


def test_repo_update_members_missing_raises() -> None:
    """
    update should raise InvalidInputException when members not found.
    """
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        None,
    ]

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(GitRepoUpdateDTO(id=1, members=[RepoMemberRefDTO(id=99)]))


def test_repo_update_clickup_space_association_by_id() -> None:
    """
    update should associate ClickUp space when id exists.
    """
    clickup_model = SimpleNamespace(id=5, name="Space", space_code="SPC", repo_id=None)
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        clickup_model,
    ]

    repo = SqlAlchemyRepoRepository(session)
    result = repo.update(
        GitRepoUpdateDTO(id=1, clickup_space=RepoClickUpSpaceRefDTO(id=5))
    )

    assert result.id == 1
    assert repo_model.clickup_space.id == 5
    session.commit.assert_called_once()


def test_repo_update_clickup_space_missing_raises() -> None:
    """
    update should raise InvalidInputException when ClickUp space not found.
    """
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        None,
    ]

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(
            GitRepoUpdateDTO(id=1, clickup_space=RepoClickUpSpaceRefDTO(id=99))
        )


def test_repo_update_members_requires_id_or_mail() -> None:
    """
    update should raise InvalidInputException when members lack id/mail.
    """
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = repo_model

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(GitRepoUpdateDTO(id=1, members=[RepoMemberRefDTO()]))


def test_repo_update_members_association_by_mail() -> None:
    """
    update should associate members when mail exists.
    """
    member_model = SimpleNamespace(id=10, username="alice", mail="a@b.com")
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        member_model,
    ]

    repo = SqlAlchemyRepoRepository(session)
    result = repo.update(
        GitRepoUpdateDTO(id=1, members=[RepoMemberRefDTO(mail="a@b.com")])
    )

    assert result.id == 1
    assert repo_model.members[0].mail == "a@b.com"
    session.commit.assert_called_once()


def test_repo_update_members_missing_mail_raises() -> None:
    """
    update should raise InvalidInputException when member mail not found.
    """
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        None,
    ]

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(GitRepoUpdateDTO(id=1, members=[RepoMemberRefDTO(mail="x@y.com")]))


def test_repo_update_clickup_space_already_associated_raises() -> None:
    """
    update should raise InvalidInputException when ClickUp space already linked to another repo.
    """
    clickup_model = SimpleNamespace(
        id=5,
        name="Space",
        space_code="SPC",
        repo_id=999,
    )
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        clickup_model,
    ]

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(
            GitRepoUpdateDTO(id=1, clickup_space=RepoClickUpSpaceRefDTO(id=5))
        )


def test_repo_update_clickup_space_association_by_space_code() -> None:
    """
    update should associate ClickUp space by space_code.
    """
    clickup_model = SimpleNamespace(id=5, name="Space", space_code="SPC", repo_id=None)
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        None,
        clickup_model,
    ]

    repo = SqlAlchemyRepoRepository(session)
    result = repo.update(
        GitRepoUpdateDTO(id=1, clickup_space=RepoClickUpSpaceRefDTO(space_code="SPC"))
    )

    assert result.id == 1
    assert repo_model.clickup_space.space_code == "SPC"
    session.commit.assert_called_once()


def test_repo_update_clickup_space_by_space_code_already_associated_raises() -> None:
    """
    update should raise InvalidInputException when space_code is linked to another repo.
    """
    clickup_model = SimpleNamespace(id=5, name="Space", space_code="SPC", repo_id=999)
    repo_model = SimpleNamespace(
        id=1,
        name="repo",
        url="https://example.com/repo",
        members=[],
        clickup_space=None,
    )
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.side_effect = [
        repo_model,
        None,
        clickup_model,
    ]

    repo = SqlAlchemyRepoRepository(session)

    with pytest.raises(InvalidInputException):
        repo.update(
            GitRepoUpdateDTO(id=1, clickup_space=RepoClickUpSpaceRefDTO(space_code="SPC"))
        )
