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
from typing import Type, TypeVar, Generic

from dotenv import load_dotenv
from openai import AzureOpenAI, APIConnectionError, APIStatusError
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from backend.src.domain.exceptions.azure.agent_initialization_exception import AgentInitializationException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.llm.llm_api_exception import LLMApiException
from backend.src.domain.exceptions.llm.llm_network_exception import LLMNetworkException
from backend.src.domain.exceptions.llm.llm_parsing_exception import LLMParsingException
from backend.src.domain.ports.services.iprompt_loader import IPromptLoader


logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[5]
_DOTENV_PATH = _BACKEND_DIR / ".env"

T = TypeVar("T")


class BaseAgent(Generic[T]):
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

    def _call_llm(
            self,
            agent_name: str,
            folder_name: str,
            prompt_name: str,
            variables: dict,
            response_format: Type[T],
    ) -> T:
        """
        Execute a structured LLM call with unified error handling.

        Loads the prompt, builds messages, calls the LLM, and returns
        the parsed response. Raises domain exceptions on failure.

        Args:
            agent_name: Agent name.
            folder_name: Prompt folder name.
            prompt_name: Prompt template name.
            variables: Variables to inject into the prompt.
            response_format: Pydantic model for structured output parsing.

        Returns:
            Parsed response of type T.

        Raises:
            LLMNetworkException: If a network error occurs while contacting the LLM.
            LLMApiException: If the LLM API returns an error response.
            LLMParsingException: If the LLM response cannot be parsed correctly.
        """
        messages = self.prompt_loader.get_messages(
            folder_name=folder_name,
            name=prompt_name,
            variables=variables,
        )
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=messages["system"]),
            ChatCompletionUserMessageParam(role="user", content=messages["user"]),
        ]

        try:
            response = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=0,
                response_format=response_format,
            )
            return response.choices[0].message.parsed


        except APIConnectionError as e:
            logger.exception("Network error contacting LLM in %s: reason=%s.", agent_name, str(e))
            raise LLMNetworkException() from e

        except APIStatusError as e:
            logger.exception("LLM API error in %s: status=%d.", agent_name, e.status_code)
            raise LLMApiException() from e


        except Exception as e:
            logger.exception("LLM call failed in %s: reason=%s.", agent_name, str(e))
            raise LLMParsingException() from e