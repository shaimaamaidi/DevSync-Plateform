"""
AI dependency container for prompt-based services.

This module defines the BaseAIContainer class, which is responsible for
initializing and exposing AI-related infrastructure components such as
prompt loading services.

It acts as a lightweight dependency container for AI-driven features
within the application (e.g., LLM prompt management, agent orchestration).

Classes:
    BaseAIContainer: Container for AI-related dependencies.
"""

import logging
from backend.src.domain.exceptions.base.app_exception import AppException
from backend.src.infrastructure.prompts.prompt_loader import PromptLoader


logger = logging.getLogger(__name__)


class BaseAIContainer:
    """
    AI dependency container.

    This container is responsible for initializing and managing AI-related
    infrastructure components required by LLM-based services.

    Currently, it provides access to:
    - Prompt loading system (PromptLoader)

    It ensures that AI dependencies are correctly initialized and available
    for application services that rely on prompt-based or LLM-based logic.
    """

    def __init__(self):
        """
        Initialize AI container dependencies.

        This constructor initializes the prompt loading system used by AI services.

        Raises:
            AppException: If the prompt loader initialization fails, indicating
            that AI services are currently unavailable.
        """
        try:
            self.prompt_loader = PromptLoader()
        except Exception as e:
            logger.exception("Failed to initialize PromptLoader.")
            raise AppException(
                "AI services are currently unavailable. Please try again later.",
                "PROMPT_LOADER_INIT_ERROR",
                http_status=500,
            ) from e