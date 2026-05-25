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
from pathlib import Path

import httpx
import asyncio
from datetime import datetime
from typing import List

from dotenv import load_dotenv

from backend.src.domain.entities.github.deployment import DeploymentDTO
from backend.src.domain.exceptions.github.github_api_exception import GitHubApiException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.ports.output.github.i_github_deployment_service import IGitHubDeploymentService
from backend.src.infrastructure.external.github.base_github_client import BaseGitHubClient

logger = logging.getLogger(__name__)


_BACKEND_DIR = Path(__file__).resolve().parents[4]
_DOTENV_PATH = _BACKEND_DIR / ".env"

DEPLOY_KEYWORDS = {"deploy", "release", "publish", "cd", "continuous-delivery", "ship"}


class GitHubDeploymentAdapter(BaseGitHubClient, IGitHubDeploymentService):
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
        BaseGitHubClient.__init__(self)
        IGitHubDeploymentService.__init__(self)
        loaded = load_dotenv(_DOTENV_PATH, override=False)

        if not loaded:
            logger.warning(".env file not found at %s.", _DOTENV_PATH)

        try:
            self.ACTIONS_MAX_RUNS = int(os.getenv("ACTIONS_MAX_RUNS",100))

            self.DEPLOYMENTS_MAX_ITEMS = int(os.getenv("DEPLOYMENTS_MAX_ITEMS",30))

        except ValueError as e:
            logger.exception(
                "Failed to parse TOKEN_CLEANUP_INTERVAL_HOURS='%s'. Expected an integer. Error: %s",
                os.getenv("TOKEN_CLEANUP_INTERVAL_HOURS"),
                e
            )
            raise MissingEnvVariableException() from e

    async def get_deployments(self, repo_url: str, max_deployments: int | None) -> List[DeploymentDTO]:
        """
        Retrieve deployments for a repository URL.

        Merges results from:
        1. GitHub Deployments API — explicit deployment events
        2. GitHub Actions runs — workflow runs with deploy-related names

        Results are deduplicated by dep_id and sorted newest-first by
        created_at string (ISO-sortable).

        Args:
            repo_url (str): GitHub repository URL.
            max_deployments (int | None): Maximum number of deployments to return.
                If None, uses the default configured limit from environment.

        Returns:
            List[DeploymentDTO]: Deduplicated, sorted list of DeploymentDTOs.

        Raises:
            InvalidGitHubUrlException: If the repository URL is malformed.
            GitHubRepoNotFoundException: If the repository does not exist.
            GitHubApiException: For network or API errors during fetch.
        """
        logger.info("Fetching all deployments for repository: %s.", repo_url)

        max_items = max_deployments or self.DEPLOYMENTS_MAX_ITEMS

        owner, repo = self._parse_repo(repo_url)

        api_deployments = await self._fetch_deployments_from_api(owner, repo, max_deployments)

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

        return merged[:max_items]

    async def get_deployments_between_dates(
        self,
        repo_url: str,
        since: datetime,
        until: datetime,
        max_deployments: int ,
    ) -> List[DeploymentDTO]:
        """
        Retrieve deployments within a date range.

        Strategy (mirrors get_commits_between_dates):
            - Paginate API + Actions newest-first
            - Stop pagination as soon as created_at goes below `since`
            - Apply max_deployments cap AFTER date filtering

        Args:
            repo_url: GitHub repository URL.
            since: Start datetime (inclusive).
            until: End datetime (inclusive).
            max_deployments: Maximum to return after date filtering.
                Defaults to DEPLOYMENTS_MAX_ITEMS.

        Returns:
            List[DeploymentDTO]: Deployments in [since, until], newest first.
        """
        logger.info(
            "Fetching deployments for %s between %s and %s (cap=%s).",
            repo_url, since.isoformat(), until.isoformat(), max_deployments,
        )

        owner, repo = self._parse_repo(repo_url)

        raw_deps, raw_runs = await asyncio.gather(
            self._fetch_raw_deployments_in_window(owner, repo, since, until),
            self._fetch_actions_in_window(owner, repo, since, until),
        )

        environments: set[str] = {
            dep.get("environment", "-") for dep in raw_deps if dep.get("environment")
        }
        status_map = await self._fetch_latest_status_per_environment(owner, repo, environments)

        api_deployments: List[DeploymentDTO] = []
        for dep in raw_deps:
            env = dep.get("environment", "-")
            state, log_url = status_map.get(env, ("no status", "-"))
            api_deployments.append(DeploymentDTO(
                dep_id=dep["id"],
                environment=env,
                ref=dep.get("ref", "-"),
                sha=dep.get("sha", "")[:7],
                creator=dep.get("creator", {}).get("login", "-"),
                created_at=datetime.fromisoformat(
                    dep.get("created_at").replace("Z", "+00:00")
                ).astimezone() if dep.get("created_at") else None,
                description=dep.get("description") or "-",
                state=state,
                log_url=log_url,
            ))

        actions_deployments: List[DeploymentDTO] = []
        for run in raw_runs:
            workflow_name = run.get("name") or run.get("display_title") or ""
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

            actions_deployments.append(DeploymentDTO(
                dep_id=run.get("id", 0),
                environment=run.get("head_branch") or "-",
                ref=run.get("head_branch") or "-",
                sha=(run.get("head_sha") or "")[:7],
                creator=(run.get("actor") or {}).get("login", "-"),
                created_at=datetime.fromisoformat(
                    run.get("created_at").replace("Z", "+00:00")
                ).astimezone() if run.get("created_at") else None,
                description=f"[Actions] {workflow_name}",
                state=state,
                log_url=run.get("html_url") or "-",
            ))

        seen_ids: set[int] = set()
        merged: List[DeploymentDTO] = []
        for dep in api_deployments + actions_deployments:
            if dep.dep_id not in seen_ids:
                seen_ids.add(dep.dep_id)
                merged.append(dep)

        merged.sort(key=lambda d: d.created_at or datetime.min, reverse=True)

        result = merged[:max_deployments]

        logger.info(
            "Found %d deployment(s) in window [%s → %s] for %s.",
            len(result), since.isoformat(), until.isoformat(), repo_url,
        )

        return result

    async def _fetch_raw_deployments_in_window(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> list[dict]:
        """
        Paginate /deployments and stop as soon as we go past `since`.

        GitHub returns deployments newest-first, so once created_at < since
        all remaining pages are also out of the window — we can stop early.

        Args:
            owner: Repository owner.
            repo: Repository name.
            since: Start datetime (inclusive).
            until: End datetime (inclusive).

        Returns:
            Raw deployment dicts whose created_at falls in [since, until].
        """
        results: list[dict] = []
        page = 1

        async with httpx.AsyncClient(timeout=self.GITHUB_TIMEOUT) as client:
            while True:
                url = (
                    f"https://api.github.com/repos/{owner}/{repo}/deployments"
                    f"?per_page=100&page={page}"
                )
                resp = await client.get(url, headers=self._get_headers())
                resp.raise_for_status()
                batch: list[dict] = resp.json()

                if not batch:
                    break

                stop = False
                for dep in batch:
                    raw_date = dep.get("created_at")
                    if not raw_date:
                        continue

                    created_at = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).astimezone()

                    if created_at < since:
                        # GitHub is newest-first — everything after is older, stop
                        stop = True
                        break

                    if created_at <= until:
                        results.append(dep)

                if stop:
                    break

                # No Link header → last page
                link = resp.headers.get("Link", "")
                if 'rel="next"' not in link:
                    break

                page += 1

        return results

    async def _fetch_actions_in_window(
        self,
        owner: str,
        repo: str,
        since: datetime,
        until: datetime,
    ) -> list[dict]:
        """
        Paginate Actions runs and stop as soon as we go past `since`.

        Same early-stop strategy as _fetch_raw_deployments_in_window.

        Args:
            owner: Repository owner.
            repo: Repository name.
            since: Start datetime (inclusive).
            until: End datetime (inclusive).

        Returns:
            Raw workflow run dicts in [since, until] with deploy-related names.
        """
        results: list[dict] = []
        page = 1

        async with httpx.AsyncClient(timeout=self.GITHUB_TIMEOUT) as client:
            while True:
                url = (
                    f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
                    f"?per_page=100&page={page}"
                )
                resp = await client.get(url, headers=self._get_headers())
                resp.raise_for_status()

                data = resp.json()
                runs: list[dict] = data.get("workflow_runs", [])

                if not runs:
                    break

                stop = False
                for run in runs:
                    raw_date = run.get("created_at")
                    if not raw_date:
                        continue

                    created_at = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).astimezone()

                    if created_at < since:
                        stop = True
                        break

                    if created_at <= until:
                        workflow_name = run.get("name") or run.get("display_title") or ""
                        if self._is_deploy_workflow(workflow_name):
                            results.append(run)

                if stop:
                    break

                link = resp.headers.get("Link", "")
                if 'rel="next"' not in link:
                    break

                page += 1

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
        self,
        owner: str,
        repo: str,
        environments: set[str]
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
        self,
        owner: str,
        repo: str,
        max_deployments: int | None
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
            max_deployments (int | None): Maximum number of deployments to return.
                If None, uses the default configured limit from environment.

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
        max_items = max_deployments or self.DEPLOYMENTS_MAX_ITEMS

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
        self,
        owner: str,
        repo: str
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