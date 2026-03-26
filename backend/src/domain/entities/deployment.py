"""Domain DTO for deployment data."""

from dataclasses import dataclass


@dataclass
class DeploymentDTO:
    """Deployment information returned by GitHub."""
    dep_id: int
    environment: str
    ref: str
    sha: str
    creator: str
    created_at: str
    description: str
    state: str
    log_url: str