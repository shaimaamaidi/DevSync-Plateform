"""
Domain adapter for GitHub commit data.

This module provides an adapter implementation for fetching and processing
GitHub commit information across repository branches. It retrieves commit
data from the GitHub API and transforms raw responses into CommitDTO objects
for downstream processing and analysis.
"""

import logging
from datetime import datetime, timezone
from typing import List

from backend.src.domain.entities.github.commit import CommitDTO
from backend.src.domain.ports.output.github.i_github_commit_service import IGitHubCommitService
from backend.src.infrastructure.external.github.base_github_client import BaseGitHubClient


logger = logging.getLogger(__name__)


class GitHubCommitsAdapter(BaseGitHubClient, IGitHubCommitService):
    """
    Adapter for fetching and managing GitHub commit data.

    This class interacts with the GitHub API to retrieve commits across
    deployed branches and converts them into structured CommitDTO objects.

    It is mainly used for:
    - Tracking code changes across environments
    - Linking commits to deployment branches
    - Supporting task/status analysis based on Git history
    """

    def __init__(self):
        """
        Initialize the GitHubCommitsAdapter.

        Inherits configuration and GitHub client setup from BaseGitHubClient.
        """
        BaseGitHubClient.__init__(self)
        IGitHubCommitService.__init__(self)

    async def get_commits_between_dates(
            self,
            repo_url: str,
            since: datetime,
            until: datetime,
            max_commits: int = 60,
    ) -> List[CommitDTO]:
        """
        Retrieve commits within a date range across deployed branches.

        This method:
            - Extracts repository owner and name from the URL
            - Fetches deployment references to identify relevant branches
            - Retrieves commits from each branch
            - Deduplicates commits by SHA
            - Sorts results by most recent commit first

        Args:
            repo_url: GitHub repository URL.
            since: Start datetime (inclusive).
            until: End datetime (inclusive).
            max_commits: Maximum number of unique commits to return.

        Returns:
            List[CommitDTO]: Unique commits sorted newest first, capped at max_commits.

        Raises:
            InvalidGitHubUrlException: If the repository URL is malformed.
            GitHubRepoNotFoundException: If the repository does not exist.
            GitHubApiException: For network or API errors during fetch.
        """
        logger.info(
            "Fetching commits for %s between %s and %s (cap=%d).",
            repo_url, since.isoformat(), until.isoformat(), max_commits,
        )

        owner, repo = self._parse_repo(repo_url)

        dep_raw = await self._github_get(
            f"https://api.github.com/repos/{owner}/{repo}/deployments?per_page=30&page=1",
            max_pages=1,
        )

        branches = list({d.get("ref") for d in dep_raw if d.get("ref") and d.get("ref") != "-"})

        if not branches:
            branches = [None]

        since_iso = since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        until_iso = until.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        all_commits: List[CommitDTO] = []
        seen_shas: set[str] = set()

        for branch in branches:
            url = (
                f"https://api.github.com/repos/{owner}/{repo}/commits"
                f"?per_page={min(max_commits, 100)}&page=1"
                f"&since={since_iso}&until={until_iso}"
            )
            if branch:
                url += f"&sha={branch}"

            raw = await self._github_get(url, max_pages=1)

            for item in raw:
                sha = (item.get("sha") or "")[:7]
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)

                commit = item.get("commit", {})
                author_data = commit.get("author") or {}
                github_author = (item.get("author") or {}).get("login", author_data.get("name", "-"))
                date_str = author_data.get("date")

                all_commits.append(CommitDTO(
                    sha=sha,
                    message=commit.get("message", "").split("\n")[0],
                    author=github_author,
                    date=datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone() if date_str else None,
                    url=item.get("html_url", "-"),
                    branch=branch,
                ))

        all_commits.sort(key=lambda c: c.date or datetime.min, reverse=True)

        logger.info(
            "Fetched %d unique commit(s) between %s and %s for %s.",
            len(all_commits), since_iso, until_iso, repo_url,
        )

        return all_commits[:max_commits]

    async def get_commits(self, repo_url: str, max_commits: int = 100) -> List[CommitDTO]:
        """
        Retrieve recent commits across deployed branches of a repository.

        This method:
        - Extracts repository owner and name from the URL
        - Fetches deployment references to identify relevant branches
        - Retrieves commits from each branch
        - Deduplicates commits by SHA
        - Sorts results by most recent commit first

        Args:
            repo_url: GitHub repository URL.
            max_commits: Maximum number of unique commits to return.

        Returns:
            List[CommitDTO]: Unique commits sorted from newest to oldest.

        Raises:
            InvalidGitHubUrlException: If the repository URL is malformed.
            GitHubRepoNotFoundException: If the repository does not exist.
            GitHubApiException: For network or API errors during fetch.
        """
        logger.info("Fetching commits for repository: %s.", repo_url)

        owner, repo = self._parse_repo(repo_url)

        dep_raw = await self._github_get(
            f"https://api.github.com/repos/{owner}/{repo}/deployments?per_page=30&page=1",
            max_pages=1,
        )
        branches = list({d.get("ref") for d in dep_raw if d.get("ref") and d.get("ref") != "-"})

        if not branches:
            branches = [None]

        all_commits = []
        seen_shas = set()

        for branch in branches:
            url = (
                f"https://api.github.com/repos/{owner}/{repo}/commits"
                f"?per_page={min(max_commits, 100)}&page=1"
            )
            if branch:
                url += f"&sha={branch}"

            raw = await self._github_get(url, max_pages=1)

            for item in raw:
                sha = (item.get("sha") or "")[:7]
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)

                commit = item.get("commit", {})
                author_data = commit.get("author") or {}
                github_author = (item.get("author") or {}).get("login", author_data.get("name", "-"))
                date_str = author_data.get("date")

                all_commits.append(CommitDTO(
                    sha=sha,
                    message=commit.get("message", "").split("\n")[0],
                    author=github_author,
                    date=datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone() if date_str else None,
                    url=item.get("html_url", "-"),
                    branch=branch,
                ))

        all_commits.sort(key=lambda c: c.date or datetime.min, reverse=True)

        logger.info(
            "Fetched %d unique commit(s) across %d branch(es) for %s.",
            len(all_commits), len(branches), repo_url,
        )

        return all_commits[:max_commits]