"""
Domain DTO for ClickUp workspace member invitation representation.

This module defines the data structures used to represent
workspace member invitations in ClickUp.

It provides a structured way to model invited members and their
assigned workspace roles while ensuring consistent validation
and transformation of invitation data when communicating with
the ClickUp API.

Main components:
    ClickUpMemberRole, ClickUpMemberInvitation
"""

from enum import IntEnum

from pydantic import BaseModel


class ClickUpMemberRole(IntEnum):
    """
    ClickUp workspace role enumeration.

    Defines the permission level assigned to a member within
    a ClickUp workspace:

    - OWNER : Full workspace control and management permissions.
    - ADMIN : Administrative access with advanced management capabilities.
    - MEMBER: Standard collaborative workspace access.
    - GUEST : Restricted or limited access to specific resources.

    Notes:
        - Role identifiers are defined by the ClickUp API.
        - MEMBER is the default role used for invitations.
        - OWNER permissions generally include billing and workspace ownership actions.
    """

    OWNER = 2
    ADMIN = 3
    MEMBER = 4
    GUEST = 5


class ClickUpMemberInvitation(BaseModel):
    """
    Domain DTO representing a ClickUp workspace member invitation.

    An invitation defines the information required to add a new
    member to a ClickUp workspace, including the target email
    address and the assigned workspace role.

    Attributes:
        email: Email address of the invited member.
        role: Workspace role assigned to the invited member
            (OWNER / ADMIN / MEMBER / GUEST).
    """

    email: str
    role: ClickUpMemberRole = ClickUpMemberRole.MEMBER