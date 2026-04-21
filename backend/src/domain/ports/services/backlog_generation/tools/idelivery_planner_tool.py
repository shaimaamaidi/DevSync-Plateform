"""
Service port for delivery planning tool.

This module defines the IDeliveryPlannerTool interface, which specifies a callable contract
for transforming a backlog into a structured delivery plan. It is designed to be used as a
tool in the sprint planning and delivery pipeline.
"""

from abc import ABC, abstractmethod


class IDeliveryPlannerTool(ABC):
    """
    Define delivery planning tool behavior required by the application.

    This interface represents a callable tool responsible for converting a backlog into a
    structured delivery plan, typically including sprint organization, estimation, and
    planning-oriented structuring.
    """

    @abstractmethod
    async def __call__(self, backlog: str) -> str:
        """
        Generate a delivery plan from a backlog.

        Args:
            backlog (str): Structured backlog as a text or serialized format.

        Returns:
            str: Generated delivery plan as a structured text or serialized output.
        """
        pass