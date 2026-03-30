"""
Domain DTO for deployment data.

This module defines the DeploymentDTO for representing deployment information returned by GitHub.

Main classes:
    DeploymentDTO
"""

from dataclasses import dataclass


@dataclass
class DeploymentDTO:
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
    dep_id: int
    environment: str
    ref: str
    sha: str
    creator: str
    created_at: str
    description: str
    state: str
    log_url: str