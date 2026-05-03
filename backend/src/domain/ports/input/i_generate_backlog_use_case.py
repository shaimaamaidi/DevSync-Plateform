"""
Use case port for backlog generation use case.

This module defines the IGenerateBacklogUseCase interface, which specifies
the contract for generating and refining project backlogs in a streaming manner.

It acts as the application layer orchestration contract for:
- Initial backlog generation from a product description
- Market intelligence interaction and refinement loop
- Backlog refinement and iterative updates
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from backend.src.domain.entities.backlog.reply_backlog_request import ReplyBacklogStreamRequest
from backend.src.domain.entities.backlog.reply_request import ReplyStreamRequest
from backend.src.domain.entities.backlog.start_request import StartBacklogRequest


class IGenerateBacklogUseCase(ABC):
    """
    Define backlog generation use case behavior required by the application.

    This interface represents the contract for orchestrating backlog generation
    workflows using streaming responses, enabling iterative refinement based on
    user feedback and market intelligence.
    """

    @abstractmethod
    async def start(self, request: StartBacklogRequest) -> AsyncGenerator[str, None]:
        """
        Start backlog generation from an initial description.

        Args:
            request (StartBacklogRequest): Initial backlog generation request.

        Returns:
            AsyncGenerator[str, None]: Stream of backlog chunks.
        """
        pass

    @abstractmethod
    async def reply(self, request: ReplyStreamRequest) -> AsyncGenerator[str, None]:
        """
        Handle market intelligence reply (validation/correction loop).

        Args:
            request (ReplyStreamRequest): User reply for market intelligence step.

        Returns:
            AsyncGenerator[str, None]: Stream of updated responses.
        """
        pass

    @abstractmethod
    async def reply_backlog(
        self, request: ReplyBacklogStreamRequest
    ) -> AsyncGenerator[str, None]:
        """
        Handle backlog refinement replies.

        Args:
            request (ReplyBacklogStreamRequest): User modifications to backlog.

        Returns:
            AsyncGenerator[str, None]: Stream of updated backlog chunks.
        """
        pass