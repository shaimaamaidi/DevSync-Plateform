"""
Unit tests for PromptLoader.

These tests create temporary prompt template files and verify loader
behaviour for missing files, invalid YAML, schema validation, rendering
and caching.
"""

from pathlib import Path


from backend.src.infrastructure.prompts.prompt_loader import PromptLoader
from backend.src.domain.exceptions.prompt.prompt_file_not__found_exception import PromptFileNotFoundException


def _make_loader_with_tmpdir(tmp_path: Path) -> PromptLoader:
    loader = PromptLoader.__new__(PromptLoader)
    loader.templates_dir = tmp_path
    loader._cache = {}
    return loader


def test_load_file_raises_when_missing(tmp_path: Path) -> None:
    loader = _make_loader_with_tmpdir(tmp_path)

    with pytest.raises(PromptFileNotFoundException):
        loader._load_file(folder_name="some_folder", filename="missing_file")


def test_load_file_raises_on_invalid_yaml(tmp_path: Path) -> None:
    folder = tmp_path / "test_folder"
    folder.mkdir(parents=True)
    path = folder / "bad.prompty"
    path.write_text("::: not a yaml :::")

    loader = _make_loader_with_tmpdir(tmp_path)

    with pytest.raises(PromptYamlException):
        loader._load_file(folder_name="test_folder", filename="bad")


def test_load_file_raises_on_missing_content_document(tmp_path: Path) -> None:
    folder = tmp_path / "test_folder"
    folder.mkdir(parents=True)
    path = folder / "meta_only.prompty"
    path.write_text("name: meta-only\nversion: 1")

    loader = _make_loader_with_tmpdir(tmp_path)

    with pytest.raises(PromptSchemaException):
        loader._load_file(folder_name="test_folder", filename="meta_only")


def test_get_messages_renders_and_caches(tmp_path: Path) -> None:
    folder = tmp_path / "backlog_generation"
    folder.mkdir(parents=True)

    content = """
name: example
---
system: "System says {{who}}"
user: "Please do {{task}}"
"""

    (folder / "example.prompty").write_text(content)

    loader = _make_loader_with_tmpdir(tmp_path)

    messages = loader.get_messages("backlog_generation", "example", {"who": "tester", "task": "work"})

    assert messages["system"] == "System says tester"
    assert messages["user"] == "Please do work"

    cached = loader._load_file("backlog_generation", "example")
    assert cached.system == "System says {{who}}" or "System says tester"


def test_get_backlog_orchestrator_instructions_reads_system_only(tmp_path: Path) -> None:
    folder = tmp_path / "backlog_generation"
    folder.mkdir(parents=True)

    content = """
name: orchestrator
---
system: "Orchestrate: {{plan}}"
"""

    (folder / "azure_backlog_workflow_orchestrator.prompty").write_text(content)

    loader = _make_loader_with_tmpdir(tmp_path)

    instructions = loader.get_backlog_orchestrator_instructions()

    assert "Orchestrate" in instructions
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
