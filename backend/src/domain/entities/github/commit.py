"""
Domain DTO for GitHub commit representation.

This module defines the CommitDTO used to represent a single GitHub commit.
It is typically used for task status analysis, traceability, and linking
code changes to application-level workflow decisions.

Main classes:
    CommitDTO
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CommitDTO:
    """
    Representation of a GitHub commit.

    This DTO encapsulates commit metadata retrieved from GitHub,
    enabling downstream services to analyze changes, track progress,
    and correlate commits with task or deployment workflows.

    Attributes:
        sha: Short commit SHA (7 characters).
        message: Full commit message describing the change.
        author: GitHub username of the commit author.
        date: Timestamp of when the commit was created.
        url: Direct URL to the commit on GitHub.
        branch: Branch name from which the commit was retrieved, if available.
    """
    sha: str
    message: str
    author: str
    date: datetime
    url: str
    branch: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Serialize commit data into a dictionary format.

        This method prepares the commit information for external usage,
        such as LLM processing, logging, or API transmission.

        Returns:
            dict: Serialized representation of the commit.
        """
        return {
            "sha": self.sha,
            "message": self.message,
            "author": self.author,
            "date": self.date.isoformat() if self.date else None,
            "url": self.url,
            "branch": self.branch,
        }