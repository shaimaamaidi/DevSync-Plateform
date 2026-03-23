import re
import requests
from datetime import datetime
from typing import List
from backend.src.domain.entities.deployment import DeploymentDTO
from backend.src.domain.ports.services.i_github_service import IGitHubService

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubDeploymentAdapter(IGitHubService):
    @staticmethod
    def _parse_repo(url: str) -> tuple[str, str]:
        url = url.rstrip("/")
        match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
        if not match:
            raise ValueError(f"URL GitHub invalide : {url}")
        return match.group(1), match.group(2)

    @staticmethod
    def _github_get(url: str):
        results = []
        while url:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset", "")
                msg = "Rate limit atteint."
                if reset:
                    reset_dt = datetime.fromtimestamp(int(reset)).strftime("%H:%M:%S")
                    msg += f" Reessayez apres {reset_dt}."
                raise PermissionError(msg)
            if resp.status_code == 404:
                raise FileNotFoundError("Repo introuvable (404).")
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                results.extend(data)
            else:
                return data
            link = resp.headers.get("Link", "")
            url = next(
                (re.search(r"<([^>]+)>", p).group(1) for p in link.split(",") if 'rel="next"' in p),
                None,
            )
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
        return deployments

    def display_deployments(self, repo_url: str) -> None:
        owner, repo = self._parse_repo(repo_url)
        deployments = self.get_deployments(repo_url)
        print(f"\n{'='*70}")
        print(f"  DEPLOYMENTS -- {owner}/{repo}  ({len(deployments)} trouvés)")
        print(f"{'='*70}\n")
        if not deployments:
            print("  Aucun deploiement trouve pour ce repo.")
            return
        for d in deployments:
            label = self._status_icon(d.state)
            print(f"  [{label:12s}]  env={d.environment}  ref={d.ref} ({d.sha})")
            print(f"      ID       : {d.dep_id}")
            print(f"      Cree par : {d.creator}  le  {d.created_at}")
            print(f"      Desc.    : {d.description}")
            print(f"      Logs     : {d.log_url}")
            print()