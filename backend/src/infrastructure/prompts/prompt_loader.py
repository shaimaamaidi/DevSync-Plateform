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
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
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


    def get_messages(self,folder_name:str, name: str, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Render prompt templates into LLM-ready messages.

        This method:
        - Loads a prompt template by name
        - Applies Jinja2 variable substitution
        - Produces system and user messages
        - Returns OpenAI-compatible message structure

        Args:
            folder_name: Folder containing the prompt template.
            name (str): Prompt template name (without `.prompty` extension).
            variables (Dict[str, Any]): Variables used to render the template.

        Returns:
            Dict[str, str]:
                Rendered messages:
                - "system": rendered system prompt
                - "user": rendered user prompt

        Raises:
            PromptRenderException: If Jinja2 rendering fails while generating system/user messages.
        """
        logger.info("Rendering prompt: %s", name)

        prompt = self._load_file(folder_name, name, has_user=True)

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

    def get_backlog_orchestrator_instructions(self) -> str:
        """
        Retrieve system-level instructions for the backlog orchestration agent.

        Loads the dedicated `.prompty` file used to configure the AI workflow
        orchestrator and extracts the system instruction block.

        Returns:
            str: System-level instruction content.
        """
        folder_name = "backlog_generation"
        filename = "azure_backlog_workflow_orchestrator"

        logger.info("Loading agent instructions from prompt: %s", folder_name + "/" + filename)
        system_instructions = self._load_file(
            folder_name=folder_name,
            filename=filename,
            has_user=False,
        )

        logger.info("Agent instructions loaded successfully from: %s", folder_name + "/" + filename)

        return system_instructions.system

    def _load_file(self, folder_name:str, filename: str, has_user: bool = True) -> Prompt:
        """
        Load and parse a `.prompty` prompt file.

        `.prompty` files follow a multi-document YAML structure:
        - Front-matter: metadata (name, description, tags, version)
        - Content: system/user prompt definitions

        This method:
        - Loads file from disk
        - Parses YAML safely (multi-document support)
        - Extracts front-matter and content sections
        - Builds a Prompt domain object
        - Caches the result for performance

        Args:
            folder_name: Folder containing the prompt file.
            filename: Prompt file name without extension.
            has_user: Whether the prompt includes a user section.

        Returns:
            Prompt: Parsed and structured prompt object containing system template, user template,
                and metadata.

        Raises:
            PromptFileNotFoundException: If the prompt file does not exist.
            PromptYamlException: If the YAML content is invalid or cannot be parsed.
            PromptSchemaException: If required fields (system or user) are missing in the prompt.
            PromptFileReadException: If file cannot be read.
        """
        cache_key = f"{folder_name}/{filename}"

        if cache_key in self._cache:
            logger.info("Prompt cache hit: %s", cache_key)
            return self._cache[cache_key]

        logger.info("Loading prompt from disk: %s", cache_key)

        file_path = self.templates_dir / folder_name / f"{filename}.prompty"

        if not os.path.exists(file_path):
            logger.error("Prompt file not found: %s", file_path)
            raise PromptFileNotFoundException(
                message=f"Prompt file not found: {file_path}",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except Exception as e:
            logger.exception("Failed to read or parse prompt file: %s", file_path)
            raise PromptFileReadException(
                message=f"Failed to read prompt file '{file_path}': {str(e)}",
            ) from e

        try:
            documents = list(yaml.safe_load_all(raw_content ))
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
            if has_user and "system" in doc and "user" in doc:
                content = doc

            elif not has_user and "system" in doc and "user" not in doc:
                content = doc
            else:
                # Treat the first non-content document as front-matter.
                if not front_matter:
                    front_matter = doc

        if not content:
            expected = "'system' and 'user'" if has_user else "'system'"
            raise PromptSchemaException(
                message=f"Invalid prompt structure in '{cache_key}': expected a document with keys {expected}.",
            )

        prompt = Prompt(
            folder=folder_name,
            name=content.get("name") or front_matter.get("name"),
            system=content["system"],
            user=content["user"] if has_user else None,
            meta={
                "description": content.get("description") or front_matter.get("description"),
                "tags": content.get("tags") or front_matter.get("tags", []),
                "version": content.get("version") or front_matter.get("version"),
            },
        )

        self._cache[cache_key] = prompt

        logger.info("Prompt loaded successfully: %s", cache_key)

        return prompt