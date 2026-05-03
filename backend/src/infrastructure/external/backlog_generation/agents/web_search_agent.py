"""
Web search agent.

This module defines the WebSearchAgent, responsible for performing parallel
web search queries using an Azure AI Agent integrated with Bing grounding.
It supports concurrent question execution and aggregates results into a
structured text response.
"""

import logging

import os
import asyncio
from typing import List

from azure.ai.agents.models import BingGroundingTool
from azure.core.exceptions import AzureError, ClientAuthenticationError, ServiceRequestError

from backend.src.domain.exceptions.azure.azure_agent_runtime_exception import AzureAgentRuntimeException
from backend.src.domain.exceptions.azure.missing_azure_config_exception import MissingAzureConfigException
from backend.src.domain.ports.services.backlog_generation.agents.iweb_search import IWebSearch
from backend.src.infrastructure.external.backlog_generation.common.azure_retry import AzureRetry
from backend.src.infrastructure.external.backlog_generation.common.base_azure_project_agent import BaseAzureProjectAgent


logger = logging.getLogger(__name__)


class WebSearchAgent(BaseAzureProjectAgent, IWebSearch):
    """
    Azure-based implementation of IWebSearch.

    This agent is responsible for:
    - Executing multiple web search queries in parallel
    - Using Azure AI Agents with Bing grounding tool
    - Aggregating and formatting search results for downstream LLM agents

    Attributes:
        bing_connection_name (str): Azure Bing grounding connection name.
        agent: Azure AI agent instance used for execution.
    """

    def __init__(self):
        """
        Initialize the WebSearchAgent.

        Loads required Azure configuration and ensures Bing connection is available.

        Raises:
            MissingAzureConfigException: If the required environment variable BING_CONNECTION_NAME
                is not defined.
        """
        super().__init__("TASK_CREATOR_WEB_SEARCH_AGENT_ID")

        self.bing_connection_name = os.environ.get("BING_CONNECTION_NAME")

        if not self.bing_connection_name:
            logger.error("Missing BING_CONNECTION_NAME environment variable.")
            raise MissingAzureConfigException("Missing Azure Agent environment variable: BING_CONNECTION_NAME.")

        self._retry = AzureRetry()

    async def create(self):
        """
        Initialize the underlying Azure agent.

        Returns:
            None: This method does not return a value; it initializes the Azure agent.
        """
        await self.load_agent()

    async def ask_many(self, questions: List[str]) -> str:
        """
        Execute multiple web search queries concurrently.

        Args:
            questions (List[str]): List of search queries.

        Returns:
            str: Aggregated search results in formatted text.

        Raises:
            AzureAgentRuntimeException: If all queries fail and no result can be returned.
        """
        logger.info("Executing %d web search queries.", len(questions))

        if not self.agent:
            logger.warning("Web Search Agent not loaded, attempting lazy load.")
            await self.load_agent()

        tasks = [self._ask_one(q) for q in questions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output_lines = []
        errors = []

        for q, res in zip(questions, results):
            if isinstance(res, Exception):
                errors.append(res)
            else:
                output_lines.append(f"Query: {q}\nResult: {res}\n")

        if len(errors) == len(questions):
            raise AzureAgentRuntimeException(
                message=f"All {len(questions)} web search queries failed. Last error: {errors[-1]}."
            )

        if errors:
            logger.warning("%d/%d queries failed but partial results returned.", len(errors), len(questions))

        logger.info("Web search completed successfully.")

        return "\n".join(output_lines)


    async def _ask_one(self, question: str) -> str:
        """
        Execute a single web search query using Azure AI Agent.

        Args:
            question (str): The search query.

        Returns:
            str: The assistant response or error message.

        Raises:
            AzureAgentRuntimeException:
                - If the agent run does not complete successfully
                - If an unexpected runtime error occurs
                - If response extraction fails
            AzureError:Raised by Azure SDK for general service-related issues
                (handled by retry mechanism).
            ClientAuthenticationError: Raised when authentication with Azure services fails
                (handled by retry mechanism).
            ServiceRequestError: Raised for network issues or timeouts (handled by retry mechanism).
        """
        if not question:
            return ""

        async def _run_once() -> str:
            thread = await self.project_client.agents.threads.create()
            try:
                await self.project_client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=question,
                )

                run = await self.project_client.agents.runs.create(
                    thread_id=thread.id,
                    agent_id=self.agent_id,
                )

                deadline = asyncio.get_event_loop().time() + self._retry.run_timeout
                while run.status in ("queued", "in_progress"):
                    if asyncio.get_event_loop().time() > deadline:
                        raise ServiceRequestError(
                            f"Run {run.id} timed out after {self._retry.run_timeout}(s)."
                        )
                    await asyncio.sleep(1)
                    run = await self.project_client.agents.runs.get(
                        thread_id=thread.id,
                        run_id=run.id,
                    )

                if run.status != "completed":
                    raise AzureAgentRuntimeException(
                        message=(
                            f"Web search run failed: status={run.status}, "
                            f"error={getattr(run, 'last_error', None)}."
                        )
                    )

                messages = await self.project_client.agents.messages.list(
                    thread_id=thread.id
                )
                async for msg in messages:
                    if msg.role == "assistant":
                        for content in msg.content:
                            if content.type == "text":
                                return content.text.value

                return "No response found"

            except (AzureError, ClientAuthenticationError, ServiceRequestError):
                logger.exception("Azure SDK error in _ask_one (will retry if eligible).")
                raise

            except AzureAgentRuntimeException:
                raise

            except Exception as e:
                logger.exception("Unexpected error in _ask_one.")
                raise AzureAgentRuntimeException(
                    message=f"Web search execution failed: {str(e)}."
                ) from e

            finally:
                try:
                    await self.project_client.agents.threads.delete(thread.id)
                except AzureError:
                    logger.warning("Failed to delete thread after attempt.")

        return await self._retry.run(_run_once)

    async def update_agent_tools(self) -> None:
        """
        Update agent configuration to use only Bing grounding tool.

        Returns:
            None: This method does not return a value; it updates the agent configuration with Bing grounding tools.

        Raises:
            MissingAzureConfigException: If the Azure connection for Bing grounding is missing
                or cannot be retrieved.
            AzureAgentRuntimeException: If an error occurs while updating the Azure agent
                configuration or tools.
        """
        logger.info("Updating web search agent tools (Bing grounding only).")

        try:
            bing_connection = await self.project_client.connections.get(
                self.bing_connection_name
            )

            if not bing_connection:
                raise MissingAzureConfigException(
                    f"Bing grounding connection '{self.bing_connection_name}' not found."
                )

            bing = BingGroundingTool(connection_id=bing_connection.id)

            instructions = """
            You are a helpful assistant with access to Bing web search.
            Use Bing grounding when the user asks for:
            - latest information
            - news
            - trends
            - factual updates
            """

            self.agent = await self.project_client.agents.update_agent(
                self.agent_id,
                tools=bing.definitions,
                instructions=instructions,
                temperature=self.agent.temperature if self.agent else 0.09,
            )

            logger.info("Web search agent tools updated successfully.")

        except (AzureError, ClientAuthenticationError, ServiceRequestError) as e:
            logger.exception("Azure SDK error updating tools.")
            raise AzureAgentRuntimeException(
                message=f"Azure error updating web search tools: {str(e)}."
            ) from e

        except Exception as e:
            logger.exception("Failed to update web search agent tools.")
            raise AzureAgentRuntimeException(
                message=f"Failed to update web search agent tools: {str(e)}."
            ) from e