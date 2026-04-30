"""
Domain model for prompt templates.

This module defines the Prompt class, which represents a rendered prompt template
used by LLM agents, including system and user messages along with metadata.

Main classes:
    Prompt
"""

from typing import Dict, Any


class Prompt:
    """
    Model representing a prompt template.

    This class encapsulates the components of a prompt used for LLM interactions,
    including system instructions, user input template, and optional metadata.

    Attributes:
        name (str): Name or identifier of the prompt.
        system (str): System-level instructions for the LLM.
        user (str): User-facing prompt content.
        meta (Dict[str, Any]): Additional metadata associated with the prompt.
    """

    def __init__(self,folder: str, name: str, system: str, user: str, meta: Dict[str, Any]):
        """
        Initialize a Prompt instance.

        Args:
            name (str): Name or identifier of the prompt.
            system (str): System-level instructions.
            user (str): User prompt content.
            meta (Dict[str, Any]): Additional metadata for the prompt.
        """
        self.folder = folder
        self.name = name
        self.system = system
        self.user = user
        self.meta = meta