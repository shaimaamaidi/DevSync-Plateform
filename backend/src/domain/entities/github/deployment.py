"""
Domain DTO for deployment data.

This module defines the DeploymentDTO for representing deployment information returned by GitHub.

Main classes:
    DeploymentDTO
"""

from datetime import datetime

from pydantic import BaseModel


class DeploymentDTO(BaseModel):
    """
    Deployment information returned by GitHub.

    Attributes:
        dep_id: Deployment identifier.
        environment: Deployment environment.
        ref: Git reference.
        sha: Commit SHA.
        creator: Creator username.
        created_at: Creation timestamp.
        description: Deployment description.
        state: Deployment state.
        log_url: URL to deployment logs.
    """
    dep_id: str
    environment: str
    ref: str
    sha: str
    creator: str
    created_at: datetime
    description: str
    state: str
    log_url: str