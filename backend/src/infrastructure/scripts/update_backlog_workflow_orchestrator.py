"""
Azure AI backlog agents update script.

This script is responsible for synchronizing all Azure AI agents related
to the backlog generation workflow.

It ensures that:
- Web search agent tools and instructions are updated on Azure
- Backlog workflow orchestrator tools are synchronized with latest domain logic
- System prompts (instructions) are refreshed from the prompt loader

This guarantees that any change in:
- domain tools
- prompt templates
- orchestration logic

is immediately reflected in the deployed Azure AI agents.

Execution flow:
1. Initialize dependency injection container
2. Initialize web search tool agent
3. Update web search agent on Azure
4. Load latest orchestrator instructions from prompt system
5. Rebuild backlog workflow orchestrator
6. Update orchestrator tools and instructions on Azure

This script is typically executed manually or during deployment pipelines.

Usage:
    python -m backend.src.infrastructure.scripts.update_backlog_agents
"""

import asyncio
import logging

from backend.src.infrastructure.di.backlog_generation_container import BacklogGenerationContainer
from backend.src.infrastructure.logging.logger_config import setup_logger


setup_logger()
logger = logging.getLogger(__name__)


async def main():
    """
    Entry point for updating Azure AI backlog-related agents.

    This function:
    - Initializes the dependency injection container
    - Updates the web search agent on Azure
    - Updates the backlog workflow orchestrator agent
    - Ensures all tools and instructions are synchronized

    Raises:
        Exception:
            Any exception raised during Azure agent update process
    """
    logger.info("Starting backlog agents update script.")

    container = BacklogGenerationContainer()

    # Web Search Agent
    await container.initialize_web_search_tool()

    logger.info("Updating web search agent tools and instructions on Azure.")

    await container.web_search_agent.update_agent_tools()

    # Backlog Workflow Orchestrator
    instructions = container.prompt_loader.get_backlog_orchestrator_instructions()
    orchestrator = await container.backlog_workflow_orchestrator_factory()

    logger.info("Updating orchestrator tools and instructions on Azure.")

    await orchestrator.update_agent_tools(instructions)

    #logger.info("Listing updated orchestrator tools.")

    #await orchestrator.list_agent_tools()

    logger.info("All backlog agents updated successfully.")


if __name__ == "__main__":
    asyncio.run(main())