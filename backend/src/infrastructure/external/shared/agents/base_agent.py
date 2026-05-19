"""
Base agent for Azure OpenAI-backed LLM agents.

This module defines the BaseAgent class, which provides shared initialization
logic for all LLM agents in the backlog generation workflow. It is responsible
for configuring the Azure OpenAI client and loading prompt templates.

All domain-specific agents inherit from this base class.
"""

import logging

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI

from backend.src.domain.exceptions.azure.agent_initialization_exception import AgentInitializationException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader


logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[5]
_DOTENV_PATH = _BACKEND_DIR / ".env"


class BaseAgent:
    """
    Base class for all LLM agents.

    This class centralizes:
    - Azure OpenAI client initialization
    - Environment variable loading and validation
    - Prompt loader injection

    Attributes:
        client (AzureOpenAI): Configured Azure OpenAI client.
        prompt_loader (IPromptLoader): Service used to load prompt templates.
        endpoint (str): Azure OpenAI endpoint.
        api_key (str): Azure OpenAI API key.
        api_version (str): API version.
        model (str): Deployment/model name.
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the base LLM agent.

        Loads environment variables, validates required Azure OpenAI configuration,
        and initializes the OpenAI client.

        Args:
            prompt_loader (IPromptLoader): Prompt loader used by all agents.

        Raises:
            MissingEnvVariableException: If required Azure OpenAI environment variables are missing.
            AgentInitializationException: If AzureOpenAI client initialization fails due to SDK error,
                invalid configuration, or unexpected runtime exception.
        """
        loaded = load_dotenv(_DOTENV_PATH, override=False)

        if not loaded:
            logger.warning(".env file not found at %s.", _DOTENV_PATH)

        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")
        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")

        required_vars = {
            "AZURE_OPENAI_ENDPOINT": self.endpoint,
            "AZURE_OPENAI_API_KEY": self.api_key,
            "AZURE_OPENAI_API_VERSION": self.api_version,
            "AZURE_OPENAI_DEPLOYMENT_NAME": self.model,
        }

        missing = [k for k, v in required_vars.items() if not v]

        if missing:
            logger.error("Missing Azure OpenAI environment variables: %s", missing)
            raise MissingEnvVariableException(
                "The AI service is not properly configured. Please contact your administrator."
            )

        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version
            )
        except Exception as e:
            logger.exception("Failed to initialize AzureOpenAI client.")
            raise AgentInitializationException(
                "The AI service could not be started. Please try again or contact support."
            ) from e

        self.prompt_loader = prompt_loader