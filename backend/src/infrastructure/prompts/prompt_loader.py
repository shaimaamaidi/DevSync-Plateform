"""
Infrastructure service for loading and rendering LLM prompt templates.

This module provides the PromptLoader implementation responsible for:
- Loading prompt templates stored in `.prompty` YAML files
- Parsing them into domain Prompt objects
- Rendering Jinja2-based templates with runtime variables
- Caching prompts to optimize performance
- Extracting system-level instructions for AI agents

It acts as the bridge between:
- Static prompt definitions (filesystem YAML templates)
- Runtime LLM-ready messages (system/user formatted outputs)
"""

import logging

import os
from pathlib import Path

import yaml
from typing import Dict, Any
from jinja2 import Template

from backend.src.domain.exceptions.prompt.prompt_file_not__found_exception import PromptFileNotFoundException
from backend.src.domain.exceptions.prompt.prompt_file_read_exception import PromptFileReadException
from backend.src.domain.exceptions.prompt.prompt_render_exception import PromptRenderException
from backend.src.domain.exceptions.prompt.prompt_schema_exception import PromptSchemaException
from backend.src.domain.exceptions.prompt.prompt_template_directory_not_found_exception import \
    PromptTemplateDirectoryNotFoundException
from backend.src.domain.exceptions.prompt.prompt_yaml_exception import PromptYamlException
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader
from backend.src.infrastructure.prompts.prompt import Prompt


logger = logging.getLogger(__name__)


class PromptLoader(IPromptLoader):
    """
    Concrete implementation of IPromptLoader.

    This class is responsible for:
    - Loading prompt templates from disk
    - Caching parsed prompts for performance
    - Rendering system and user templates using Jinja2
    - Extracting agent system instructions from prompt files

    Attributes:
        templates_dir (Path): Directory where `.prompty` template files are stored.
        _cache (Dict[str, Prompt]): In-memory cache of loaded Prompt objects to avoid repeated I/O.
    """

    def __init__(self):
        """
        Initialize PromptLoader.

        Responsibilities:
        - Resolve templates directory path
        - Validate existence of templates directory
        - Initialize in-memory cache

        Raises:
            PromptTemplateDirectoryNotFoundException: If templates directory does not exist.
        """
        current_dir = Path(__file__).parent
        self.templates_dir = current_dir / "templates"

        if not self.templates_dir.exists():
            raise PromptTemplateDirectoryNotFoundException(
                f"Templates directory not found: {self.templates_dir}",
            )

        self._cache: Dict[str, Prompt] = {}


    def get_messages(self, name: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Render prompt templates into LLM-ready messages.

        This method:
        - Loads a prompt template by name
        - Applies Jinja2 variable substitution
        - Produces system and user messages
        - Returns OpenAI-compatible message structure

        Args:
            name (str): Prompt template name (without `.prompty` extension).
            variables (Dict[str, Any]): Variables used to render the template.

        Returns:
            Dict[str, str]:
                Rendered messages:
                - "system": rendered system prompt
                - "user": rendered user prompt

        Raises:
            PromptFileNotFoundException: If the prompt template file does not exist.
            PromptYamlException: If YAML parsing fails while loading the prompt file.
            PromptSchemaException:  If the prompt structure is invalid or missing required fields.
            PromptRenderException: If Jinja2 rendering fails while generating system/user messages.
        """
        logger.info("Rendering prompt: %s", name)

        prompt = self._load_file(name)

        try:
            system_rendered = Template(prompt.system).render(**variables)
            user_rendered = Template(prompt.user).render(**variables)

            logger.info("Prompt rendered successfully: %s", name)

            return {
                "system": system_rendered,
                "user": user_rendered
            }
        except Exception as e:
            logger.exception("Failed to render prompt: %s", name)
            raise PromptRenderException(
                message=f"Failed to render prompt '{name}': {str(e)}",
            ) from e

    def get_agent_instructions(self) -> str:
        """
        Retrieve system-level instructions for AI agent configuration.

        Reads the `azure_backlog_workflow_orchestrator.prompty` file which follows
        the two-document YAML Prompty spec:
          - Document 1: front-matter (name, description, model, tags…)
          - Document 2: content block with `system` key

        Uses yaml.safe_load_all to handle the multi-document format instead of
        naive string splitting, which breaks when the word "system:" appears
        inside the prompt body itself.

        Returns:
            str: System instruction text used by the AI agent.

        Raises:
            PromptTemplateDirectoryNotFoundException: If the templates directory does not exist.
            PromptFileNotFoundException: If the agent instruction prompt file does not exist.
            PromptFileReadException: If the prompt file cannot be read from disk.
            PromptYamlException: If the YAML content is invalid or cannot be parsed.
            PromptSchemaException: If no document with a 'system' key is found.
        """
        prompt_name = "azure_backlog_workflow_orchestrator"

        logger.info("Loading agent instructions from prompt: %s", prompt_name)

        file_path = self.templates_dir / f"{prompt_name}.prompty"

        if not file_path.exists():
            logger.error("Prompt file not found: %s", file_path)
            raise PromptFileNotFoundException(
                message=f"Prompt file not found: {file_path}",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                documents = list(yaml.safe_load_all(f))
        except Exception as e:
            logger.exception("Failed to read or parse prompt file: %s", file_path)
            raise PromptFileReadException(
                message=f"Failed to read prompt file '{file_path}': {str(e)}",
            ) from e

        # Find the document that contains the `system` key (the content block).
        # The front-matter block (metadata) does not have a `system` key.
        system_instructions: str | None = None
        for doc in documents:
            if isinstance(doc, dict) and "system" in doc:
                system_instructions = doc["system"]
                break

        if system_instructions is None:
            logger.error("No 'system' key found in any YAML document in prompt: %s", prompt_name)
            raise PromptSchemaException(
                message=f"Invalid prompt structure in '{prompt_name}': no document with a 'system' key found.",
            )

        logger.info("Agent instructions loaded successfully from: %s", prompt_name)

        return system_instructions

    def _load_file(self, filename: str) -> Prompt:
        """
        Load a prompt template from a `.prompty` YAML file.

        .prompty files follow the Prompty spec: they contain TWO YAML documents
        separated by `---`:
          1. A front-matter block with metadata (name, description, model, tags…)
          2. A content block with `system` and `user` keys

        yaml.safe_load only accepts a single document, so we use
        yaml.safe_load_all to iterate over both and pick the one that contains
        the required `system` / `user` keys.

        Args:
            filename (str): Name of the prompt file without `.prompty` extension.

        Returns:
            Prompt: Domain object containing system template, user template, and metadata.

        Raises:
            PromptFileNotFoundException: If the prompt file does not exist.
            PromptYamlException: If the YAML content is invalid or cannot be parsed.
            PromptSchemaException: If required fields (system or user) are missing in the prompt.
        """
        if filename in self._cache:
            logger.info("Prompt cache hit: %s", filename)
            return self._cache[filename]

        logger.info("Loading prompt from disk: %s", filename)

        file_path = os.path.join(self.templates_dir, f"{filename}.prompty")

        if not os.path.exists(file_path):
            logger.error("Prompt file not found: %s", file_path)
            raise PromptFileNotFoundException(
                message=f"Prompt file not found: {file_path}",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # safe_load_all handles multi-document YAML (separated by ---)
                # which is the standard .prompty file format.
                documents = list(yaml.safe_load_all(f))
        except Exception as e:
            logger.exception("Failed to parse YAML prompt file: %s", file_path)
            raise PromptYamlException(
                message=f"Invalid YAML in prompt file '{file_path}': {str(e)}",
            ) from e

        if not documents:
            raise PromptYamlException(
                message=f"Empty YAML file: {file_path}"
            )

        # The front-matter block contains metadata (name, description, model…).
        # The content block contains `system` and `user` keys.
        # We support both single-document files (legacy) and two-document .prompty files.
        front_matter: dict = {}
        content: dict = {}

        for doc in documents:
            if not isinstance(doc, dict):
                continue
            if "system" in doc and "user" in doc:
                content = doc
            else:
                # Treat the first non-content document as front-matter.
                if not front_matter:
                    front_matter = doc

        if not content:
            raise PromptSchemaException(
                message=f"Invalid prompt structure in '{filename}': expected a document with keys 'system' and 'user'.",
            )

        prompt = Prompt(
            name=content.get("name") or front_matter.get("name"),
            system=content["system"],
            user=content["user"],
            meta={
                "description": content.get("description") or front_matter.get("description"),
                "tags":        content.get("tags")        or front_matter.get("tags", []),
                "version":     content.get("version")     or front_matter.get("version"),
            },
        )

        self._cache[filename] = prompt

        logger.info("Prompt loaded successfully: %s", filename)

        return prompt