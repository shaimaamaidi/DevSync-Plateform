"""
Backlog prioritizer agent.

This module defines the BacklogPrioritizerAgent, responsible for prioritizing
and restructuring a structured backlog using LLM-based reasoning.

The agent transforms a raw backlog into a prioritized and enriched version by:
- Assigning stable identifiers to tasks
- Preserving task descriptions via internal mapping
- Reordering and restructuring backlog content using LLM intelligence
- Rebuilding a clean, structured backlog aligned with domain entities

It ensures traceability between original tasks and LLM-processed output.
"""

import uuid
import logging

from backend.src.domain.entities.backlog.structure import BacklogStructure,EpicBacklog, UserStoryWithTasks
from backend.src.domain.entities.backlog.structure_with_identified_tasks import BacklogStructureWithIdentifiedTasks, \
    UserStoryWithIdentifiedTasks, EpicBacklogWithIdentifiedTasks
from backend.src.domain.entities.backlog.task import IdentifiedTask, Task
from backend.src.domain.ports.services.backlog_generation.agents.i_backlog_prioritizer import IBacklogPrioritizer
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class BacklogPrioritizerAgent(BaseAgent[BacklogStructureWithIdentifiedTasks], IBacklogPrioritizer):
    """
    LLM-based implementation of IBacklogPrioritizer.

    This agent is responsible for:
    - Prioritizing backlog content using LLM reasoning
    - Assigning stable identifiers to tasks for traceability
    - Preserving original task descriptions via mapping
    - Reconstructing a structured and ordered backlog

    The process combines:
    - Deterministic UUID assignment for tasks
    - LLM-based prioritization and restructuring
    - Post-processing reconstruction of original task details
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the BacklogPrioritizerAgent.

        This constructor sets up the agent with the required prompt loading
        service used to retrieve LLM prompt templates.

        The prompt loader is responsible for:
        - Loading prioritization prompts
        - Providing structured templates for LLM calls
        - Ensuring consistency across backlog processing steps

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def prioritize(self, backlog: BacklogStructure) -> BacklogStructure:
        """
        Prioritize and restructure a backlog using LLM-based reasoning.

        This method transforms a raw backlog into a prioritized version by:
        - Assigning unique identifiers to tasks
        - Sending structured backlog to an LLM for prioritization
        - Reconstructing original task descriptions after LLM processing
        - Returning a clean, ordered backlog structure

        Processing steps:
        1. Convert backlog into identified format with UUIDs
        2. Build task description lookup table
        3. Send identified backlog to LLM for prioritization
        4. Receive prioritized backlog structure from LLM
        5. Restore original task descriptions using lookup
        6. Rebuild final BacklogStructure object

        Args:
            backlog (BacklogStructure): Raw backlog containing epics,
                user stories, and tasks to be prioritized.

        Returns:
            BacklogStructure: Prioritized backlog with original structure
                and restored task descriptions.

        Logs:
            - Start and completion of prioritization process
            - Missing task descriptions (warnings)
        """
        logger.info("Starting backlog prioritization process.")

        identified_backlog, task_desc_lookup = BacklogPrioritizerAgent._build_identified_backlog(backlog)

        result: BacklogStructureWithIdentifiedTasks = self._call_llm(
            agent_name="BacklogPrioritizerAgent",
            folder_name="backlog_generation",
            prompt_name="backlog_prioritizer_agent",
            variables={
                "backlog": identified_backlog,
            },
            response_format=BacklogStructureWithIdentifiedTasks,
        )

        epics = []
        for epic_block in result.epics:
            user_stories = []
            for us_block in epic_block.user_stories:
                tasks = []
                for task in us_block.tasks:
                    tasks.append(Task(
                        title=task.title,
                        description=task_desc_lookup.get(task.id, "")
                    ))
                    if not task_desc_lookup.get(task.id):
                        logger.warning("Task description not found for task_id: %s", task.id)
                user_stories.append(UserStoryWithTasks(
                    user_story=us_block.user_story,
                    tasks=tasks
                ))
            epics.append(EpicBacklog(
                epic=epic_block.epic,
                user_stories=user_stories
            ))

        logger.info("Backlog prioritization completed successfully.")
        return BacklogStructure(epics=epics)

    @staticmethod
    def _build_identified_backlog(
            backlog: BacklogStructure,
    ) -> tuple[BacklogStructureWithIdentifiedTasks, dict[str, str]]:
        """
        Convert a standard backlog into an identified backlog with stable task IDs.

        This method replaces raw tasks with IdentifiedTask objects containing
        UUIDs, allowing traceability between original and LLM-processed data.

        It also builds a lookup dictionary to recover original task descriptions
        after LLM processing.

        Processing steps:
        1. Traverse all epics → user stories → tasks
        2. Assign UUID to each task
        3. Store original descriptions in lookup dictionary
        4. Replace tasks with IdentifiedTask (empty description for LLM input)
        5. Build identified backlog structure

        Args:
            backlog (BacklogStructure): Original structured backlog.

        Returns:
            tuple:
                - BacklogStructureWithIdentifiedTasks: backlog with UUID-based tasks
                - dict[str, str]: mapping of task_id → original description

        Notes:
            - UUID ensures traceability across LLM transformations
            - Descriptions are stripped before LLM input to avoid bias
        """
        task_desc_lookup: dict[str, str] = {}
        identified_epics = []

        for epic_block in backlog.epics:
            identified_stories = []
            for us_block in epic_block.user_stories:
                identified_tasks = []
                for task in us_block.tasks:
                    task_id = str(uuid.uuid4())
                    task_desc_lookup[task_id] = task.description
                    identified_tasks.append(IdentifiedTask(
                        id=task_id,
                        title=task.title,
                        description="",
                    ))
                identified_stories.append(UserStoryWithIdentifiedTasks(
                    user_story=us_block.user_story,
                    tasks=identified_tasks,
                ))
            identified_epics.append(EpicBacklogWithIdentifiedTasks(
                epic=epic_block.epic,
                user_stories=identified_stories,
            ))

        return BacklogStructureWithIdentifiedTasks(epics=identified_epics), task_desc_lookup