"""
Domain DTO for delivery plan generation request.

This module defines the DeliveryPlanRequest DTO used to trigger the
delivery planning workflow from a validated backlog. It carries the
conversation thread identifier along with the confirmed backlog content
required to generate the final delivery plan.

Main classes:
    DeliveryPlanRequest
"""

from pydantic import BaseModel, Field


class DeliveryPlanRequest(BaseModel):
    """
    Request payload for delivery plan generation.

    This DTO is used once a backlog has been reviewed and confirmed.
    It allows the system to generate a delivery plan based on the
    finalized backlog while maintaining the existing conversation thread.

    Attributes:
        thread_id: Identifier of the conversation thread.
        backlog: Confirmed backlog content used as input for delivery
            plan generation.
    """
    thread_id: str = Field(..., min_length=1, description="Conversation thread identifier.")
    backlog: str = Field(..., description="Confirmed backlog content used to generate the delivery plan.")