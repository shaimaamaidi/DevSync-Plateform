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


class GitHubDeploymentAdapter(IGitHubService):
    @staticmethod
    def _parse_repo(url: str) -> tuple[str, str]:
        logger.info("Parsing GitHub repository URL: %s", url)

        url = url.rstrip("/")
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)

        if not match:
            logger.warning("Invalid GithHub repository URL: %s", url)
            raise InvalidGitHubUrlException(url)

        owner, repo = match.group(1), match.group(2)

        logger.info("Parsed owner=%s, repo=%s", owner, repo)

        return owner, repo

    @staticmethod
    def _github_get(url: str):
        logger.info("Fetching data from GitHub API: %s", url)

        results = []
        while url:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
            except requests.exceptions.Timeout:
                logger.error("GitHub API request timed out: %s", url)
                raise AppException(
                    message="GitHub API request timed out.",
                    code="GITHUB_TIMEOUT",
                    http_status=504
                )
            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to GitHub API: %s", url)
                raise AppException(
                    message="Could not connect to GitHub API.",
                    code="GITHUB_CONNECTION_ERROR",
                    http_status=503
                )
            if resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset", "")
                reset_dt = datetime.fromtimestamp(int(reset)).strftime("%H:%M:%S") if reset else None

                logger.warning("GitHub rate limit hit, reset at %s", reset_dt)

                raise GitHubRateLimitException(reset_dt)

            if resp.status_code == 404:
                logger.warning("GitHub Repository not found at %s", url)
                raise GitHubRepoNotFoundException(url)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(
                    "GitHub API returned HTTP error: %s",
                    str(e),
                    exc_info=e
                )
                raise AppException(
                    message=f"GitHub API error: {e}",
                    code="GITHUB_API_ERROR",
                    http_status=502
                ) from e

            data = resp.json()

            if isinstance(data, list):
                results.extend(data)
            else:
                logger.info("Fetched single object from GitHub API: %s", url)
                return data

            link = resp.headers.get("Link", "")
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    m = re.search(r"<([^>]+)>", part)
                    if m:
                        url = m.group(1)
                    break

        logger.info("GitHub API fetch completed, items fetched: %s", len(results))

        return results

    @staticmethod
    def _fmt_date(iso: str | None) -> str:
        if not iso:
            return "-"
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            return iso

    @staticmethod
    def _status_icon(state: str) -> str:
        return {
            "success": "OK", "active": "ACTIF", "failure": "ECHEC",
            "error": "ERREUR", "pending": "EN ATTENTE", "in_progress": "EN COURS",
            "queued": "FILE", "inactive": "INACTIF", "destroyed": "SUPPRIME",
        }.get(state, "?")

    def get_deployments(self, repo_url: str) -> List[DeploymentDTO]:
        logger.info("Fetching deployments for repository: %s", repo_url)

        owner, repo = self._parse_repo(repo_url)
        raw = self._github_get(f"https://api.github.com/repos/{owner}/{repo}/deployments")
        deployments = []
        for dep in raw:
            dep_id = dep["id"]
            statuses = self._github_get(
                f"https://api.github.com/repos/{owner}/{repo}/deployments/{dep_id}/statuses"
            )
            state = statuses[0].get("state", "no status") if statuses else "no status"
            log_url = (statuses[0].get("log_url") or statuses[0].get("target_url") or "-") if statuses else "-"
            deployments.append(DeploymentDTO(
                dep_id=dep_id,
                environment=dep.get("environment", "-"),
                ref=dep.get("ref", "-"),
                sha=dep.get("sha", "")[:7],
                creator=dep.get("creator", {}).get("login", "-"),
                created_at=self._fmt_date(dep.get("created_at")),
                description=dep.get("description") or "-",
                state=state,
                log_url=log_url,
            ))

        logger.info("Fetched %d deployments fro repository: %s", len(deployments), repo_url)

        return deployments