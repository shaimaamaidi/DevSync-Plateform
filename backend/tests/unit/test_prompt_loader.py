"""
Unit tests for PromptLoader and Prompt model.
"""

from pathlib import Path

import pytest

from backend.src.domain.exceptions.prompt.prompt_render_exception import PromptRenderException
from backend.src.domain.exceptions.prompt.prompt_schema_exception import PromptSchemaException
from backend.src.domain.exceptions.prompt.prompt_yaml_exception import PromptYamlException
from backend.src.infrastructure.prompts.prompt import Prompt
from backend.src.infrastructure.prompts.prompt_loader import PromptLoader


def test_prompt_model_stores_fields() -> None:
    """
    Prompt should store fields as-is.
    """
    prompt = Prompt(folder="sample", name="p", system="s", user="u", meta={"v": 1})

    assert prompt.name == "p"
    assert prompt.system == "s"
    assert prompt.user == "u"
    assert prompt.meta["v"] == 1


def test_prompt_loader_get_messages_renders(tmp_path: Path) -> None:
    """
    get_messages should render system/user templates.
    """
    loader = PromptLoader()
    templates_dir = tmp_path / "templates"
    loader.templates_dir = templates_dir
    folder_dir = templates_dir / "sample"
    folder_dir.mkdir(parents=True, exist_ok=True)
    (folder_dir / "sample.prompty").write_text(
        "---\nname: sample\n---\nsystem: \"Hello {{ name }}\"\nuser: \"Hi {{ name }}\"\n",
        encoding="utf-8",
    )

    messages = loader.get_messages("sample", "sample", {"name": "Alice"})

    assert messages["system"] == "Hello Alice"
    assert messages["user"] == "Hi Alice"


def test_prompt_loader_get_messages_render_error(tmp_path: Path) -> None:
    """
    get_messages should raise PromptRenderException when rendering fails.
    """
    loader = PromptLoader()
    templates_dir = tmp_path / "templates"
    loader.templates_dir = templates_dir
    folder_dir = templates_dir / "sample"
    folder_dir.mkdir(parents=True, exist_ok=True)
    (folder_dir / "sample.prompty").write_text(
        "---\nname: sample\n---\nsystem: \"{{\"\nuser: \"u\"\n",
        encoding="utf-8",
    )

    with pytest.raises(PromptRenderException):
        loader.get_messages("sample", "sample", {})


def test_prompt_loader_load_file_invalid_schema(tmp_path: Path) -> None:
    """
    _load_file should raise PromptSchemaException for missing fields.
    """
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    folder_dir = templates_dir / "sample"
    folder_dir.mkdir(parents=True, exist_ok=True)
    file_path = folder_dir / "bad.prompty"
    file_path.write_text("name: test\n", encoding="utf-8")

    loader = PromptLoader()
    loader.templates_dir = templates_dir

    with pytest.raises(PromptSchemaException):
        loader._load_file("sample", "bad")


def test_prompt_loader_load_file_invalid_yaml(tmp_path: Path) -> None:
    """
    _load_file should raise PromptYamlException for invalid YAML.
    """
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    folder_dir = templates_dir / "sample"
    folder_dir.mkdir(parents=True, exist_ok=True)
    file_path = folder_dir / "bad.prompty"
    file_path.write_text("bad: [", encoding="utf-8")

    loader = PromptLoader()
    loader.templates_dir = templates_dir

    with pytest.raises(PromptYamlException):
        loader._load_file("sample", "bad")
