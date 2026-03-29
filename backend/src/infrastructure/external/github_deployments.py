"""GitHub adapter for deployment data."""

import logging
import re
import requests
from datetime import datetime
from typing import List
from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.exceptions.app_exception import AppException
from backend.src.domain.exceptions.github_rate_limit_exception import GitHubRateLimitException
from backend.src.domain.exceptions.github_repo_not_found_exception import GitHubRepoNotFoundException
from backend.src.domain.exceptions.invalid_github_url_exception import InvalidGitHubUrlException
from backend.src.domain.ports.services.i_github_service import IGitHubService


logger = logging.getLogger(__name__)


HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# (connect_timeout, read_timeout) in seconds.
# connect_timeout : time to establish the TCP connection.
# read_timeout    : time to wait for the first byte once connected.
# Large repos (e.g. vercel/next.js) can be slow — keep read_timeout generous.
GITHUB_TIMEOUT: tuple[int, int] = (10, 60)

# Maximum number of recent Actions runs to inspect per request.
# Fetching all pages of large repos (thousands of runs) causes cascading
# connect-timeouts. 100 most-recent runs is sufficient to surface active deploys.
ACTIONS_MAX_RUNS: int = 100

# Maximum number of deployments fetched from the Deployments API.
# Large repos (e.g. tiangolo/fastapi) have 400+ entries spread over many pages.
# Fetching all of them + their individual status requests causes cascading
# connect-timeouts. 30 most-recent deployments is enough to surface active ones.
DEPLOYMENTS_MAX_ITEMS: int = 30

# Keywords used to detect deploy-related workflow runs from GitHub Actions
DEPLOY_KEYWORDS = {"deploy", "release", "publish", "cd", "continuous-delivery", "ship"}


class GitHubDeploymentAdapter(IGitHubService):
    """Fetch deployment data from GitHub Deployments API and GitHub Actions."""

    @staticmethod
    def _parse_repo(url: str) -> tuple[str, str]:
        """Parse owner and repository name from a GitHub URL.

        Args:
            url: GitHub repository URL.

        Returns:
            Tuple of (owner, repo).

        Raises:
            InvalidGitHubUrlException: When the URL is not a GitHub repo URL.
        """
        logger.info("Parsing GitHub repository URL: %s.", url)

        url = url.rstrip("/")
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)

        if not match:
            logger.warning("Invalid GitHub repository URL: %s.", url)
            raise InvalidGitHubUrlException(url)

        owner, repo = match.group(1), match.group(2)
        logger.info("Parsed owner=%s, repo=%s.", owner, repo)
        return owner, repo

    @staticmethod
    def _github_get(url: str, max_pages: int = 0):
        """Perform paginated GET requests against the GitHub API.

        Returns:
            API response data (list or dict).

        Args:
            url:       GitHub API URL.
            max_pages: Maximum pages to follow (0 = unlimited).

        Raises:
            AppException: For timeouts, connection, or API failures.
            GitHubRateLimitException: When rate limit is exceeded.
            GitHubRepoNotFoundException: When repository is missing.
        """
        logger.info("Fetching data from GitHub API: %s.", url)

        results = []
        page_count = 0
        while url:
            if max_pages and page_count >= max_pages:
                logger.info(
                    "Reached max_pages=%d for %s, stopping pagination.",
                    max_pages, url,
                )
                break
            page_count += 1
            try:
                resp = requests.get(url, headers=HEADERS, timeout=GITHUB_TIMEOUT)
            except requests.exceptions.Timeout:
                logger.error("GitHub API request timed out: %s.", url)
                raise AppException(
                    message="GitHub API request timed out.",
                    code="GITHUB_TIMEOUT",
                    http_status=504,
                )
            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to GitHub API: %s.", url)
                raise AppException(
                    message="Could not connect to GitHub API.",
                    code="GITHUB_CONNECTION_ERROR",
                    http_status=503,
                )

            if resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset", "")
                reset_dt = (
                    datetime.fromtimestamp(int(reset)).strftime("%H:%M:%S")
                    if reset
                    else None
                )
                logger.warning("GitHub rate limit hit, reset at %s.", reset_dt)
                raise GitHubRateLimitException(reset_dt)

            if resp.status_code == 404:
                logger.warning("GitHub resource not found at %s.", url)
                raise GitHubRepoNotFoundException(url)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error("GitHub API returned HTTP error: %s.", str(e))
                raise AppException(
                    message=f"GitHub API error: {e}",
                    code="GITHUB_API_ERROR",
                    http_status=502,
                ) from e

            data = resp.json()

            if isinstance(data, list):
                results.extend(data)
            else:
                logger.info("Fetched single object from GitHub API: %s.", url)
                return data

            # Follow pagination via Link header
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
    def _fmt_date(iso: str | None) -> str:
        """Format an ISO datetime string for display.

        Args:
            iso: ISO timestamp string.

        Returns:
            Formatted timestamp or fallback string.
        """
        if not iso:
            return "-"
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            return iso

    @staticmethod
    def _status_icon(state: str) -> str:
        """Map a deployment state to a short label.

        Args:
            state: Deployment state string.

        Returns:
            Short status label.
        """
        return {
            "success": "OK",
            "active": "ACTIF",
            "failure": "ECHEC",
            "error": "ERREUR",
            "pending": "EN ATTENTE",
            "in_progress": "EN COURS",
            "queued": "FILE",
            "inactive": "INACTIF",
            "destroyed": "SUPPRIME",
        }.get(state, "?")

    @staticmethod
    def _is_deploy_workflow(workflow_name: str) -> bool:
        """Check whether a workflow name looks deploy-related.

        Args:
            workflow_name: The workflow name from GitHub Actions.

        Returns:
            True if any deploy keyword matches.
        """
        name_lower = workflow_name.lower()
        return any(keyword in name_lower for keyword in DEPLOY_KEYWORDS)

    def _fetch_latest_status_per_environment(
        self, owner: str, repo: str, environments: set[str]
    ) -> dict[str, tuple[str, str]]:
        """Fetch the latest deployment status for each environment in one pass.

        Instead of firing N individual /statuses requests (one per deployment),
        we query /deployments?environment=X for each distinct environment and
        read the first result — GitHub returns deployments newest-first, so
        result[0] is always the most-recent deployment for that environment.
        Then we fetch its single latest status.

        This reduces N sequential requests to 2 × len(environments) requests,
        which for typical repos is 2–6 calls instead of 30.

        Args:
            owner:        Repository owner.
            repo:         Repository name.
            environments: Set of environment names found in the deployments list.

        Returns:
            Dict mapping environment name → (state, log_url).
        """
        result: dict[str, tuple[str, str]] = {}

        for env in environments:
            env_deps = self._github_get(
                f"https://api.github.com/repos/{owner}/{repo}/deployments"
                f"?environment={requests.utils.quote(env)}&per_page=1&page=1",
                max_pages=1,
            )
            if not env_deps:
                result[env] = ("no status", "-")
                continue

            dep_id = env_deps[0]["id"]
            statuses = self._github_get(
                f"https://api.github.com/repos/{owner}/{repo}/deployments/{dep_id}/statuses"
                f"?per_page=1&page=1",
                max_pages=1,
            )
            if statuses:
                state = statuses[0].get("state", "no status")
                log_url = (
                    statuses[0].get("log_url")
                    or statuses[0].get("target_url")
                    or "-"
                )
            else:
                state, log_url = "no status", "-"

            result[env] = (state, log_url)

        logger.info(
            "Resolved statuses for %d environment(s) in %s/%s: %s.",
            len(result), owner, repo,
            {e: s for e, (s, _) in result.items()},
        )
        return result

    def _fetch_deployments_from_api(
        self, owner: str, repo: str, max_items: int = DEPLOYMENTS_MAX_ITEMS
    ) -> List[DeploymentDTO]:
        """Fetch deployments from the GitHub Deployments API.

        Uses a two-step strategy to avoid N×status-request rate-limit storms:

        Step 1 — fetch the N most-recent deployment entries (1 request).
        Step 2 — resolve the latest status per *environment* (2 requests per
                 distinct environment), not per deployment. For a repo with
                 3 environments and 30 deployments this is 6 requests instead
                 of 30, and the count is bounded by the number of environments,
                 not the number of deployments.

        Args:
            owner:     Repository owner.
            repo:      Repository name.
            max_items: Maximum deployments to retrieve (default 30).

        Returns:
            List of DeploymentDTOs built from the Deployments API.
        """
        logger.info(
            "Fetching GitHub Deployments API for %s/%s (cap=%d).",
            owner, repo, max_items,
        )

        per_page = min(max_items, 100)
        raw = self._github_get(
            f"https://api.github.com/repos/{owner}/{repo}/deployments"
            f"?per_page={per_page}&page=1",
            max_pages=1,
        )
        raw = raw[:max_items] if isinstance(raw, list) else []

        if not raw:
            logger.info("Deployments API returned 0 entries for %s/%s.", owner, repo)
            return []

        # Collect distinct environments so we can batch-resolve their statuses
        environments: set[str] = {
            dep.get("environment", "-") for dep in raw if dep.get("environment")
        }
        logger.info(
            "Found %d distinct environment(s) for %s/%s: %s.",
            len(environments), owner, repo, environments,
        )

        # 2 requests per environment instead of 1 per deployment
        status_map = self._fetch_latest_status_per_environment(owner, repo, environments)

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
                    created_at=self._fmt_date(dep.get("created_at")),
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

    def _fetch_deployments_from_actions(
        self, owner: str, repo: str, max_runs: int = ACTIONS_MAX_RUNS
    ) -> List[DeploymentDTO]:
        """Fetch deploy-related workflow runs from GitHub Actions.

        Only workflow runs whose name contains a deploy-related keyword
        (e.g. deploy, release, publish, cd) are included.

        We intentionally cap the fetch to the N most recent runs
        (``max_runs``, default ``ACTIONS_MAX_RUNS``) to avoid hammering the
        API and triggering connect-timeouts on large repositories that have
        thousands of historical runs.

        Args:
            owner:    Repository owner.
            repo:     Repository name.
            max_runs: Maximum number of recent runs to inspect (default 100).

        Returns:
            List of DeploymentDTOs built from Actions workflow runs.
        """
        logger.info(
            "Fetching GitHub Actions workflow runs for %s/%s (cap=%d).",
            owner, repo, max_runs,
        )

        # /actions/runs returns {"total_count": N, "workflow_runs": [...]}
        # We only need the most-recent page — one request is enough.
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
            f"?per_page={min(max_runs, 100)}&page=1"
        )
        data = self._github_get(url)

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

            # Map GitHub Actions conclusion/status → our state vocabulary
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
                    # Actions runs have no "environment" by default; use the
                    # target branch as a human-readable substitute.
                    environment=run.get("head_branch") or "-",
                    ref=run.get("head_branch") or "-",
                    sha=(run.get("head_sha") or "")[:7],
                    creator=(run.get("actor") or {}).get("login", "-"),
                    created_at=self._fmt_date(run.get("created_at")),
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

    def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        """Retrieve deployments for a repository URL.

        Merges results from:
        1. GitHub Deployments API   — explicit deployment events
        2. GitHub Actions runs      — workflow runs with deploy-related names

        Results are deduplicated by dep_id and sorted newest-first by
        created_at string (ISO-sortable).

        Args:
            repo_url: GitHub repository URL.

        Returns:
            Deduplicated, sorted list of DeploymentDTOs.
        """
        logger.info("Fetching all deployments for repository: %s.", repo_url)

        owner, repo = self._parse_repo(repo_url)

        # --- Source 1: Deployments API ---
        api_deployments = self._fetch_deployments_from_api(owner, repo)

        # --- Source 2: GitHub Actions ---
        actions_deployments = self._fetch_deployments_from_actions(owner, repo)

        # Merge and deduplicate by dep_id (Deployments API IDs and Actions run
        # IDs live in different namespaces so collisions are practically impossible,
        # but we guard anyway).
        seen_ids: set[int] = set()
        merged: List[DeploymentDTO] = []

        for dep in api_deployments + actions_deployments:
            if dep.dep_id not in seen_ids:
                seen_ids.add(dep.dep_id)
                merged.append(dep)

        # Sort newest-first; created_at is formatted as "YYYY-MM-DD HH:MM UTC"
        # which is lexicographically sortable.
        merged.sort(key=lambda d: d.created_at, reverse=True)

        logger.info(
            "Total deployments after merge for %s: %d "
            "(%d from Deployments API, %d from Actions).",
            repo_url,
            len(merged),
            len(api_deployments),
            len(actions_deployments),
        )

        return merged