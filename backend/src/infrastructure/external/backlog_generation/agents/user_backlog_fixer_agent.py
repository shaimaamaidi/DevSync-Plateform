"""
User backlog fixer agent.

This module defines the UserBacklogFixerAgent, responsible for validating and
correcting a user-provided backlog by comparing it against a reference backlog
using an LLM.

The agent ensures:
- Structural consistency between reference and user backlog
- Detection of missing or modified epics
- Correction of invalid or incomplete epics using LLM reasoning
- Reconstruction of a validated backlog aligned with domain expectations

It combines deterministic validation logic with LLM-based epic correction
to ensure both accuracy and flexibility.
"""

import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
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
    - Detecting missing, modified, or inconsistent epics
    - Using LLM reasoning to correct invalid epics
    - Reconstructing a validated and coherent backlog structure

    The process combines:
    - Deterministic comparison of backlog structures
    - Parallel LLM validation per epic
    - Aggregation of corrections into a final validated backlog
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

        This method compares the reference backlog with the user-provided backlog,
        detects missing or inconsistent epics, and uses LLM-based validation to
        correct them.

        Processing steps:
        1. Compare epics between reference and user backlog
        2. Identify missing epics (restored directly from reference)
        3. Validate existing epics using parallel LLM calls
        4. Aggregate corrections and reconstructed epics
        5. Build final BacklogValidation result

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
            - Missing epics are restored directly without LLM intervention
            - Existing epics are validated independently in parallel
            - Final backlog preserves reference ordering
        """
        logger.info("Starting user backlog validation process.")

        missing_epics = []
        epics_to_validate = []

        for ref_epic in backlog_reference.epics:
            user_epic = next(
                (e for e in backlog_to_validate.epics
                 if e.epic.title == ref_epic.epic.title), None
            )
            if user_epic is None:
                missing_epics.append(ref_epic)
            else:
                epics_to_validate.append((ref_epic, user_epic))

        llm_results = {}
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._validate_epic, ref_epic, user_epic): ref_epic
                for ref_epic, user_epic in epics_to_validate
            }
            for future in as_completed(futures):
                ref_epic, result = future.result()
                llm_results[ref_epic.epic.title] = result

        all_corrections = []
        corrected_epics = []
        global_is_valid = True

        for ref_epic in backlog_reference.epics:
            if ref_epic in missing_epics:
                corrected_epics.append(ref_epic)
                all_corrections.append(
                    f"Restored the missing '{ref_epic.epic.title}' "
                    f"epic from the reference backlog."
                )
                global_is_valid = False
            else:
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
        """
        return ref_epic, self._call_llm(
            agent_name="UserBacklogFixerAgent",
            folder_name="backlog_generation",
            prompt_name="user_backlog_fixer_agent",
            variables={
                "reference_epic": format_epic(ref_epic),
                "user_epic": format_epic(user_epic),
            },
            response_format=EpicValidation,
        )