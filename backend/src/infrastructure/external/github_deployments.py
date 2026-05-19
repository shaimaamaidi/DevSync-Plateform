"""
GitHub adapter for deployment data.

This module provides an adapter implementation for fetching and processing
GitHub deployment information, including data from both the GitHub API and
GitHub Actions workflows.

It handles URL parsing, API requests, deployment extraction, and converts
raw GitHub data into DeploymentDTO objects suitable for further processing.
"""

import logging

import os
import re
from pathlib import Path

import httpx
import asyncio
from datetime import datetime, timezone
from typing import List

from dotenv import load_dotenv

from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.exceptions.github.github_api_exception import GitHubApiException
from backend.src.domain.exceptions.github.github_rate_limit_exception import GitHubRateLimitException
from backend.src.domain.exceptions.github.github_repo_not_found_exception import GitHubRepoNotFoundException
from backend.src.domain.exceptions.github.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.ports.output.i_github_service import IGitHubService


logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[3]
_DOTENV_PATH = _BACKEND_DIR / ".env"

DEPLOY_KEYWORDS = {"deploy", "release", "publish", "cd", "continuous-delivery", "ship"}


class GitHubDeploymentAdapter(IGitHubService):
    """
    Adapter for fetching and managing GitHub repository deployments.

    This class interacts with the GitHub API and GitHub Actions workflows
    to retrieve deployment information and transform it into DeploymentDTOs.

    Attributes:
        GITHUB_TIMEOUT (httpx.Timeout): Timeout configuration for HTTP requests, specifying connect and read timeouts in seconds.
        ACTIONS_MAX_RUNS (int): Maximum number of GitHub Actions workflow runs to fetch.
        DEPLOYMENTS_MAX_ITEMS (int): Maximum number of deployments to fetch from GitHub Deployments API.
        GITHUB_TOKEN (str): Personal access token for authenticating GitHub API requests.
    """

    def __init__(self):
        """
        Initialize the GitHubDeploymentAdapter.

        Loads environment variables, sets up API timeouts, maximum items to fetch,
        and GitHub token. Raises an exception if the required GITHUB_TOKEN is missing.

        Raises:
            MissingEnvVariableException: If the GITHUB_TOKEN environment variable is not set.
        """
        loaded = load_dotenv(_DOTENV_PATH, override=False)

        if not loaded:
            logger.warning(".env file not found at %s.", _DOTENV_PATH)

        try:
            CONNECT_TIMEOUT = int(os.getenv("CONNECT_TIMEOUT",10))
            READ_TIMEOUT = int(os.getenv("READ_TIMEOUT",60))

            self.ACTIONS_MAX_RUNS = int(os.getenv("ACTIONS_MAX_RUNS",100))

            self.DEPLOYMENTS_MAX_ITEMS = int(os.getenv("DEPLOYMENTS_MAX_ITEMS",30))

        except ValueError as e:
            logger.exception(
                "Failed to parse TOKEN_CLEANUP_INTERVAL_HOURS='%s'. Expected an integer. Error: %s",
                os.getenv("TOKEN_CLEANUP_INTERVAL_HOURS"),
                e
            )
            raise MissingEnvVariableException() from e

        self.GITHUB_TIMEOUT = httpx.Timeout(connect=CONNECT_TIMEOUT, read=READ_TIMEOUT, write=READ_TIMEOUT, pool=CONNECT_TIMEOUT)

        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

        if not self.GITHUB_TOKEN:
            logger.error("Missing required environment variable: GITHUB_TOKEN")
            raise MissingEnvVariableException()

    @staticmethod
    def _parse_repo(url: str) -> tuple[str, str]:
        """
        Parse the GitHub repository URL to extract owner and repository name.

        Args:
            url (str): Full URL of the GitHub repository.

        Returns:
            tuple[str, str]: Tuple of (owner, repository name).

        Raises:
            InvalidGitHubUrlException: If the URL format is invalid or cannot be parsed.
        """
        logger.info("Parsing GitHub repository URL: %s.", url)

        url = url.rstrip("/")
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)

        if not match:
            logger.warning("Invalid GitHub repository URL: %s.", url)
            raise InvalidGitHubUrlException()

        owner, repo = match.group(1), match.group(2)

        logger.info("Parsed owner=%s, repo=%s.", owner, repo)

        return owner, repo

    async def _github_get(self, url: str, max_pages: int = 0) -> list[dict]:
        """
        Perform an authenticated GET request to the GitHub API, handling pagination.

        Args:
            url (str): GitHub API endpoint URL.
            max_pages (int): Maximum number of pages to fetch (0 = unlimited).

        Returns:
            list[dict]: Aggregated list of results from all pages.

        Raises:
            GitHubRepoNotFoundException: If the repository or endpoint returns 404.
            GitHubRateLimitException: If the GitHub API rate limit is exceeded.
            GitHubApiException: For other HTTP errors or request failures.
        """
        logger.info("Fetching data from GitHub API: %s.", url)

        results = []
        page_count = 0
        MAX_RETRIES = 3  # number of times to retry on rate limit

        async with httpx.AsyncClient(timeout=self.GITHUB_TIMEOUT) as client:
            while url:
                if max_pages and page_count >= max_pages:
                    logger.info(
                        "Reached max_pages=%d for %s, stopping pagination.",
                        max_pages, url,
                    )
                    break

                page_count += 1
                retries = 0

                while retries <= MAX_RETRIES:
                    try:
                        resp = await client.get(url, headers=self._get_headers())
                        resp.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 404:
                            logger.warning("GitHub resource not found at %s.", url)
                            raise GitHubRepoNotFoundException()
                        if e.response.status_code == 403:
                            reset = e.response.headers.get("X-RateLimit-Reset")
                            if reset:
                                reset_time = max(int(reset) - int(datetime.now(timezone.utc).timestamp()), 1)
                                logger.warning(
                                    "GitHub rate limit hit, sleeping %d seconds before retry...", reset_time
                                )
                                await asyncio.sleep(reset_time)
                                retries += 1
                                if retries > MAX_RETRIES:
                                    raise GitHubRateLimitException() from e
                                continue
                        logger.exception("GitHub API HTTP error: %s", str(e))
                        raise GitHubApiException() from e

                    except httpx.RequestError as e:
                        logger.exception("GitHub API request failed: %s", str(e))
                        raise GitHubApiException() from e

                try:
                    data = resp.json()

                except Exception as e:
                    logger.exception("Failed to decode JSON from %s: %s", url, e)
                    raise GitHubApiException("Failed to process the response. Please try again.") from e

                if isinstance(data, list):
                    results.extend(data)
                else:
                    logger.info("Fetched single object from GitHub API: %s.", url)
                    results.append(data)

                link = resp.headers.get("Link", "")
                url = None
                for part in link.split(","):
                    if 'rel="next"' in part:
                        m = re.search(r"<([^>]+)>", part)
                        if m:
                            url = m.group(1)
                        break

        logger.info("GitHub API fetch completed, %d items fetched.", len(results))

        return results

    @staticmethod
    def _is_deploy_workflow(workflow_name: str) -> bool:
        """
        Check whether a workflow name looks deploy-related.

        Args:
            workflow_name (str): The workflow name from GitHub Actions.

        Returns:
            bool: True if any deploy keyword matches.
        """
        name_lower = workflow_name.lower()
        return any(keyword in name_lower for keyword in DEPLOY_KEYWORDS)

    async def _fetch_latest_status_per_environment(
        self, owner: str, repo: str, environments: set[str]
    ) -> dict[str, tuple[str, str]]:
        """
        Fetch the latest deployment status for each environment in one pass.

        Instead of firing N individual /statuses requests (one per deployment),
        we query /deployments?environment=X for each distinct environment and
        read the first result — GitHub returns deployments newest-first, so
        result[0] is always the most-recent deployment for that environment.
        Then we fetch its single latest status.

        This reduces N sequential requests to 2 × len(environments) requests,
        which for typical repos is 2–6 calls instead of 30.

        Args:
            owner (str): Repository owner.
            repo (str): Repository name.
            environments (set[str]): Set of environment names found in the deployments list.

        Returns:
            Dict mapping environment name → (state, log_url).
        """
        result: dict[str, tuple[str, str]] = {}

        async def fetch_env(env: str):
            MAX_RETRIES = 3
            retries = 0

            while retries <= MAX_RETRIES:
                try:
                    env_deps = await self._github_get(
                        f"https://api.github.com/repos/{owner}/{repo}/deployments?environment={env}&per_page=1&page=1",
                        max_pages=1
                    )

                    if not env_deps:
                        result[env] = ("no status", "-")
                        return

                    dep_id = env_deps[0]["id"]
                    statuses = await self._github_get(
                        f"https://api.github.com/repos/{owner}/{repo}/deployments/{dep_id}/statuses?per_page=1&page=1",
                        max_pages=1
                    )

                    if statuses:
                        state = statuses[0].get("state", "no status")
                        log_url = statuses[0].get("log_url") or statuses[0].get("target_url") or "-"
                    else:
                        state, log_url = "no status", "-"

                    result[env] = (state, log_url)
                    return

                except GitHubApiException as e:
                    retries += 1
                    if retries > MAX_RETRIES:
                        result[env] = ("error", "-")
                        logger.error("Failed to fetch deployment status for env %s after %d retries: %s", env,
                                     MAX_RETRIES, e)
                    else:
                        await asyncio.sleep(2 ** retries)

        await asyncio.gather(*(fetch_env(env) for env in environments))
        return result

    async def _fetch_deployments_from_api(
        self, owner: str, repo: str
    ) -> List[DeploymentDTO]:
        """
        Fetch deployments from the GitHub Deployments API.

        Uses a two-step strategy to avoid N×status-request rate-limit storms:

        Step 1 — fetch the N most-recent deployment entries (1 request).
        Step 2 — resolve the latest status per *environment* (2 requests per
                 distinct environment), not per deployment. For a repo with
                 3 environments and 30 deployments this is 6 requests instead
                 of 30, and the count is bounded by the number of environments,
                 not the number of deployments.

        Args:
            owner (str): Repository owner.
            repo (str): Repository name.

        Returns:
            List[DeploymentDTO]: List of DeploymentDTOs built from the Deployments API.

        Raises:
            GitHubRepoNotFoundException: If the repository does not exist.
            GitHubApiException: For network or API errors during fetch.
        """
        logger.info(
            "Fetching GitHub Deployments API for %s/%s (cap=%d).",
            owner, repo, self.DEPLOYMENTS_MAX_ITEMS,
        )
        max_items = self.DEPLOYMENTS_MAX_ITEMS

        per_page = min(max_items, 100)
        raw = await self._github_get(
            f"https://api.github.com/repos/{owner}/{repo}/deployments"
            f"?per_page={per_page}&page=1",
            max_pages=1,
        )
        raw = raw[:max_items] if isinstance(raw, list) else []

        if not raw:
            logger.info("Deployments API returned 0 entries for %s/%s.", owner, repo)
            return []

        environments: set[str] = {
            dep.get("environment", "-") for dep in raw if dep.get("environment")
        }

        logger.info(
            "Found %d distinct environment(s) for %s/%s: %s.",
            len(environments), owner, repo, environments,
        )

        status_map = await self._fetch_latest_status_per_environment(owner, repo, environments)

        deployments: List[DeploymentDTO] = []
        for dep in raw:
            env = dep.get("environment", "-")
            state, log_url = status_map.get(env, ("no status", "-"))
            deployments.append(
                DeploymentDTO(
                    dep_id=dep["id"],
                    environment=env,
                    ref=dep.get("ref", "-"),
                    sha=dep.get("sha", "")[:7],
                    creator=dep.get("creator", {}).get("login", "-"),
                    created_at=datetime.fromisoformat(dep.get("created_at").replace("Z", "+00:00")).astimezone() if dep.get("created_at") else None,
                    description=dep.get("description") or "-",
                    state=state,
                    log_url=log_url,
                )
            )

        logger.info(
            "Deployments API returned %d entries for %s/%s (cap=%d, %d env requests).",
            len(deployments), owner, repo, max_items, len(environments) * 2,
        )

        return deployments

    async def _fetch_deployments_from_actions(
        self, owner: str, repo: str
    ) -> List[DeploymentDTO]:
        """
        Fetch deploy-related workflow runs from GitHub Actions.

        Only workflow runs whose name contains a deploy-related keyword
        (e.g. deploy, release, publish, cd) are included.

        We intentionally cap the fetch to the N most recent runs
        (``max_runs``, default ``ACTIONS_MAX_RUNS``) to avoid hammering the
        API and triggering connect-timeouts on large repositories that have
        thousands of historical runs.

        Args:
            owner (str): Repository owner.
            repo (str): Repository name.

        Returns:
            List[DeploymentDTO]: List of DeploymentDTOs built from Actions workflow runs.

        Raises:
            GitHubRepoNotFoundException: If the repository or workflows do not exist.
            GitHubApiException: For API errors during workflow fetch.
        """
        logger.info(
            "Fetching GitHub Actions workflow runs for %s/%s (cap=%d).",
            owner, repo, self.ACTIONS_MAX_RUNS,
        )

        max_runs = self.ACTIONS_MAX_RUNS

        url = (
            f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
            f"?per_page={min(max_runs, 100)}&page=1"
        )

        data = await self._github_get(url)

        if isinstance(data, dict):
            runs: list = data.get("workflow_runs", [])
            total_count: int = data.get("total_count", 0)
        else:
            runs = data
            total_count = len(runs)

        logger.info(
            "Fetched %d/%d Actions runs for %s/%s (single page, cap=%d).",
            len(runs), total_count, owner, repo, max_runs,
        )

        deployments: List[DeploymentDTO] = []

        for run in runs:
            workflow_name: str = run.get("name") or run.get("display_title") or ""

            if not self._is_deploy_workflow(workflow_name):
                continue  # Skip non-deploy workflows

            conclusion = run.get("conclusion") or ""
            status = run.get("status") or ""

            if conclusion == "success":
                state = "success"
            elif conclusion in ("failure", "timed_out"):
                state = "failure"
            elif conclusion == "cancelled":
                state = "inactive"
            elif status in ("in_progress", "queued", "waiting"):
                state = status
            else:
                state = conclusion or status or "no status"

            run_id: int = run.get("id", 0)
            html_url: str = run.get("html_url") or "-"

            deployments.append(
                DeploymentDTO(
                    dep_id=run_id,
                    environment=run.get("head_branch") or "-",
                    ref=run.get("head_branch") or "-",
                    sha=(run.get("head_sha") or "")[:7],
                    creator=(run.get("actor") or {}).get("login", "-"),
                    created_at=datetime.fromisoformat(run.get("created_at").replace("Z", "+00:00")).astimezone() if run.get("created_at") else None,
                    description=f"[Actions] {workflow_name}",
                    state=state,
                    log_url=html_url,
                )
            )

        logger.info(
            "Actions returned %d deploy-related runs for %s/%s.",
            len(deployments),
            owner,
            repo,
        )

        return deployments

    async def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """
        Retrieve deployments for a repository URL.

        Merges results from:
        1. GitHub Deployments API   — explicit deployment events
        2. GitHub Actions runs      — workflow runs with deploy-related names

        Results are deduplicated by dep_id and sorted newest-first by
        created_at string (ISO-sortable).

        Args:
            repo_url (str): GitHub repository URL.

        Returns:
            List[DeploymentDTO]: Deduplicated, sorted list of DeploymentDTOs.

        Raises:
            InvalidGitHubUrlException: If the repository URL is malformed.
            GitHubRepoNotFoundException: If the repository does not exist.
            GitHubApiException: For network or API errors during fetch.
        """
        logger.info("Fetching all deployments for repository: %s.", repo_url)

        owner, repo = self._parse_repo(repo_url)

        api_deployments = await self._fetch_deployments_from_api(owner, repo)

        actions_deployments = await self._fetch_deployments_from_actions(owner, repo)

        seen_ids: set[int] = set()
        merged: List[DeploymentDTO] = []

        for dep in api_deployments + actions_deployments:
            if dep.dep_id not in seen_ids:
                seen_ids.add(dep.dep_id)
                merged.append(dep)

        merged.sort(key=lambda d: d.created_at or datetime.min, reverse=True)

        logger.info(
            "Total deployments after merge for %s: %d "
            "(%d from Deployments API, %d from Actions).",
            repo_url,
            len(merged),
            len(api_deployments),
            len(actions_deployments),
        )

        return merged

    def _get_headers(self) -> dict:
        return {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"token {self.GITHUB_TOKEN}",
        }