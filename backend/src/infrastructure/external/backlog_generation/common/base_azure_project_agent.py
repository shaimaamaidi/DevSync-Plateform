"""
Base class for all Azure AI agents in backlog generation.

This module defines BaseAzureProjectAgent, which provides shared initialization
and lifecycle management for all Azure AI agents and orchestrators used in the
backlog generation workflow.
"""

import logging

from azure.core.exceptions import AzureError
from azure.identity.aio import ClientSecretCredential
from azure.ai.projects.aio import AIProjectClient

from backend.src.domain.exceptions.azure.azure_agent_runtime_exception import AzureAgentRuntimeException
from backend.src.infrastructure.config.settings import settings


logger = logging.getLogger(__name__)


class BaseAzureProjectAgent:
    """
    Shared base class for Azure AI agents.

    This class centralizes:
    - Azure authentication (ClientSecretCredential)
    - AIProjectClient initialization
    - Agent loading lifecycle
    - Async cleanup handling

    Attributes:
        agent_id (str): Azure agent identifier loaded from environment.
        credential (ClientSecretCredential): Azure authentication credential.
        project_client (AIProjectClient): Azure AI project client.
        agent: Loaded Azure agent instance (initialized lazily).
    """

    def __init__(self, agent_id_env_key: str):
        """
        Initialize Azure base agent configuration.

        Args:
            agent_id_env_key (str): Environment variable key that contains the agent ID.

        Raises:
            MissingAzureConfigException: If one or more required Azure environment variables are
                missing (tenant_id, client_id, client_secret, endpoint, or agent_id).
            AzureAgentRuntimeException: If initialization of Azure credentials or project client fails.
        """
        tenant_id = settings.AZURE_TENANT_ID
        client_id = settings.AZURE_CLIENT_ID
        client_secret = settings.AZURE_CLIENT_SECRET
        endpoint = settings.AZURE_PROJECT_ENDPOINT
        self.agent_id = getattr(settings, agent_id_env_key, None)

        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

        self.project_client = AIProjectClient(
            endpoint=endpoint,
            credential=self.credential,
        )

        self.agent = None


    async def load_agent(self) -> None:
        """
        Load Azure agent definition from Azure AI project.

        Returns:
            None: This method does not return a value; it loads the agent into memory.

        Raises:
            AzureAgentRuntimeException: If the Azure AI agent cannot be retrieved from the project client
                due to Azure SDK failure, network issue, invalid configuration, or unexpected runtime error.
        """
        try:
            self.agent = await self.project_client.agents.get_agent(
                agent_id=self.agent_id
            )

        except AzureError as e:
            logger.exception("Azure SDK error during agent init.")
            raise AzureAgentRuntimeException(
                message="The AI service is currently unavailable. Please try again or contact support."
            ) from e

        except Exception as e:
            logger.exception("Unexpected error during agent init")
            raise AzureAgentRuntimeException(
                message="The AI service is currently unavailable. Please try again or contact support."
            ) from e

    async def cleanup(self) -> None:
        """
        Close Azure async clients and release resources.

        Returns:
            None: This method does not return a value; it closes network clients.
        """
        for closeable, name in [
            (self.project_client, "project_client"),
            (self.credential, "credential"),
        ]:
            try:
                await closeable.close()
            except Exception:
                logger.warning(
                    "Failed to close %s (agent_id=%s) — resource will be GC'd.",
                    name,
                    self.agent_id,
                )

        logger.info("Azure resources cleaned up (agent_id=%s).", self.agent_id)

    async def __aenter__(self):
        """
        Enter async context manager.

        Returns:
            BaseAzureProjectAgent: The current instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit async context manager and cleanup resources.

        Returns:
            None: This method does not return a value; it ensures cleanup of resources.
        """
        await self.cleanup()
        return False