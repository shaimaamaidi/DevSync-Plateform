"""
Service port for prompt loading.

This module defines the IPromptLoader interface, which specifies operations for loading,
rendering, and preparing prompt templates (e.g., .prompty files) for LLM-based agents.
"""

from abc import abstractmethod, ABC
from typing import Dict, Any


class IPromptLoader(ABC):
    """
    Define prompt loading behavior required by the application.

    This interface is responsible for retrieving prompt templates by name, injecting variables,
    and returning structured messages ready to be consumed by LLM APIs.
    """

    @abstractmethod
    def get_messages(
        self,
        folder_name: str,
        name: str,
        variables: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Load and render prompt messages.

        This method retrieves a prompt template (without extension), applies variable
        substitution, and returns formatted messages ready for LLM usage.

        Args:
            folder_name: Folder containing the prompt template.
            name (str): Prompt file name without extension.
            variables (Dict[str, Any]): Variables used to render the prompt.

        Returns:
            Dict[str, str]: Dictionary containing rendered messages (e.g., system and user prompts).
        """
        pass

    @abstractmethod
    def get_backlog_orchestrator_instructions(self) -> str:
        """
        Retrieve the global system instructions for an LLM agent.

        This method returns the main instruction prompt used to configure
        the behavior, constraints, and reasoning rules of an AI agent.

        Unlike `get_messages`, this method is not template-based and does not
        perform variable substitution. It provides a static or centrally-managed
        instruction set used across multiple agents or workflows.

        Returns:
            str:
                The full system instruction prompt defining the agent behavior,
                including rules, constraints, and workflow guidelines.

        Notes:
            - Typically used to initialize Azure/OpenAI agent system prompts.
            - Can be overridden to load instructions from external files or config.
        """
        pass