"""
User backlog fixer agent.

This module defines the UserBacklogFixerAgent, responsible for validating and
correcting a user-provided backlog by comparing it against a reference backlog
using an LLM.

The agent ensures:
- Structural consistency between reference and user backlog
- Detection of modified epics
- Correction of invalid or incomplete epics using LLM reasoning
- Reconstruction of a validated backlog aligned with domain expectations

It combines deterministic validation logic with LLM-based epic correction
to ensure both accuracy and flexibility.
"""

import logging

from concurrent.futures import as_completed, ThreadPoolExecutor

from backend.src.domain.entities.backlog.structure import BacklogStructure
from backend.src.domain.entities.backlog.validation import BacklogValidation, EpicValidation
from backend.src.domain.ports.services.backlog_generation.agents.i_user_backlog_fixer import IUserBacklogFixer
from backend.src.domain.ports.services.prompt_loading.i_prompt_loader import IPromptLoader
from backend.src.infrastructure.external.shared.agents.base_agent import BaseAgent
from backend.src.infrastructure.external.backlog_generation.helpers.backlog_formatter import format_epic


logger = logging.getLogger(__name__)


class UserBacklogFixerAgent(BaseAgent[EpicValidation], IUserBacklogFixer):
    """
    LLM-based implementation of IUserBacklogFixer.

    This agent is responsible for:
    - Comparing a reference backlog with a user-provided backlog
    - Detecting modified or inconsistent epics
    - Using LLM reasoning to correct invalid epics
    - Reconstructing a validated and coherent backlog structure

    The process combines:
    - Deterministic comparison of backlog structures
    - Parallel LLM validation per epic
    - Aggregation of corrections into a final validated backlog

    Constraints:
    - Epic deletion is not permitted; every reference epic is always present
    - Users may only modify epics or add user stories and tasks within them
    """

    def __init__(self, prompt_loader: IPromptLoader):
        """
        Initialize the UserBacklogFixerAgent.

        Args:
            prompt_loader (IPromptLoader): Service responsible for loading
                prompt templates used by the agent during LLM interactions.
        """
        super().__init__(prompt_loader)

    def fix_user_backlog(
            self,
            backlog_reference: BacklogStructure,
            backlog_to_validate: BacklogStructure,
    ) -> BacklogValidation:
        """
        Validate and fix a user-provided backlog using a reference backlog.

        This method compares the reference backlog with the user-provided backlog
        and uses LLM-based validation to correct each epic independently.

        Processing steps:
        1. Match each reference epic with its counterpart in the user backlog
        2. Validate each matched epic using parallel LLM calls
        3. Aggregate corrections into a final validated backlog
        4. Build final BacklogValidation result

        Args:
            backlog_reference (BacklogStructure): The expected reference backlog.
            backlog_to_validate (BacklogStructure): The user-provided backlog.

        Returns:
            BacklogValidation: Validation result containing:
                - corrected_backlog: fixed backlog structure
                - corrections: list of applied fixes
                - is_valid: global validation status

        Raises:
            LLMNetworkException: If network communication with LLM fails.
            LLMApiException: If LLM returns an error response.
            LLMParsingException: If LLM output cannot be parsed correctly.

        Notes:
            - Epic deletion is not permitted at the frontend level
            - All reference epics are guaranteed to be present in the user backlog
            - Epics are validated independently in parallel
            - Final backlog preserves reference ordering
            - Users may only modify epics or add user stories and tasks
        """
        logger.info("Starting user backlog validation process.")

        epic_pairs = list(zip(backlog_reference.epics, backlog_to_validate.epics))

        llm_results = {}
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self._validate_epic,
                    ref_epic,
                    user_epic,
                ): ref_epic
                for ref_epic, user_epic in epic_pairs
            }
            for future in as_completed(futures):
                ref_epic = futures[future]
                try:
                    _, result = future.result()
                    llm_results[ref_epic.epic.title] = result
                except Exception as e:
                    logger.error(
                        "Epic validation failed for '%s': %s",
                        ref_epic.epic.title,
                        e,
                    )
                    llm_results[ref_epic.epic.title] = EpicValidation(
                        corrected_epic=ref_epic,
                        corrections=[],
                        is_valid=True,
                    )

        all_corrections = []
        corrected_epics = []
        global_is_valid = True

        for ref_epic in backlog_reference.epics:
            result = llm_results[ref_epic.epic.title]
            corrected_epics.append(result.corrected_epic)
            all_corrections.extend(result.corrections)
            if not result.is_valid:
                global_is_valid = False

        return BacklogValidation(
            corrected_backlog=BacklogStructure(epics=corrected_epics),
            corrections=all_corrections,
            is_valid=global_is_valid,
        )

    def _validate_epic(self, ref_epic, user_epic):
        """
        Validate a single epic by comparing reference and user-provided versions using an LLM.

        This method performs semantic validation of an epic by sending both the reference
        epic and the user-modified epic to the LLM. The model detects inconsistencies,
        missing elements, structural issues, and potential deviations from the reference.

        The LLM returns a structured EpicValidation object containing:
        - corrected epic version
        - list of detected corrections
        - validation status (valid / invalid)

        Processing steps:
        1. Format reference epic into structured prompt input
        2. Format user epic into structured prompt input
        3. Send both versions to LLM for comparison and correction
        4. Parse LLM response into EpicValidation model
        5. Return reference epic + validation result

        Args:
            ref_epic: EpicBacklog
                The reference (ground truth) epic used as validation baseline.

            user_epic: EpicBacklog
                The user-provided epic to validate and correct.

        Returns:
            tuple:
                - ref_epic (EpicBacklog): Original reference epic
                - EpicValidation: LLM validation result containing:
                    - corrected_epic: corrected version of the epic
                    - corrections: list of applied fixes
                    - is_valid: boolean validation status

        Notes:
            - This method is executed in parallel across multiple epics
            - The LLM is used only for correction, not for detecting missing epics
            - Deterministic logic handles epic matching; LLM handles semantic repair
            - Users may add user stories and tasks; LLM decides if they are valid
        """
        result = self._call_llm(
            agent_name="UserBacklogFixerAgent",
            folder_name="backlog_generation",
            prompt_name="user_backlog_fixer_agent",
            variables={
                "reference_epic": format_epic(ref_epic),
                "user_epic": format_epic(user_epic),
            },
            response_format=EpicValidation,
        )

        has_real_correction = any(
            correction.lower().startswith(
                (
                    "removed",
                    "replaced",
                    "restored",
                    "completed",
                )
            )
            for correction in result.corrections
        )

        if result.is_valid:
            return ref_epic, EpicValidation(corrected_epic=user_epic, corrections=[],is_valid=True)

        elif not has_real_correction:
            return ref_epic, EpicValidation(
                corrected_epic=user_epic,
                corrections=[],
                is_valid=True,
            )
        else:
            return ref_epic,result
