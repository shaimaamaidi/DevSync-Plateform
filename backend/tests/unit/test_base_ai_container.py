"""
Unit tests for BaseAIContainer.
"""

from unittest.mock import MagicMock

import pytest

from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.di import bas_ai_container
from backend.src.infrastructure.di.bas_ai_container import BaseAIContainer


def test_base_ai_container_initializes_prompt_loader(monkeypatch) -> None:
    """
    Test that the AI container wires the prompt loader dependency.
    """
    prompt_loader = MagicMock()
    monkeypatch.setattr(bas_ai_container, "PromptLoader", lambda: prompt_loader)

    container = BaseAIContainer()

    assert container.prompt_loader is prompt_loader


def test_base_ai_container_wraps_prompt_loader_failure(monkeypatch) -> None:
    """
    Test that the AI container raises an application error when prompt loading setup fails.
    """
    monkeypatch.setattr(bas_ai_container, "PromptLoader", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(AppException):
        BaseAIContainer()