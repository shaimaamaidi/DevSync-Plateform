"""
Unit tests for Prompt.
"""

from backend.src.infrastructure.prompts.prompt import Prompt


def test_prompt_stores_values() -> None:
    """
    Test that Prompt stores its fields as provided.
    """
    prompt = Prompt(folder="weekly_project_summarization", name="weekly_commits", system="sys", user="usr", meta={"version": 1})

    assert prompt.folder == "weekly_project_summarization"
    assert prompt.name == "weekly_commits"
    assert prompt.system == "sys"
    assert prompt.user == "usr"
    assert prompt.meta["version"] == 1