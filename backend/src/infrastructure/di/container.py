from backend.src.application.services.member_service import MemberService
from backend.src.infrastructure.external.github_deployments import GitHubDeploymentAdapter
from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.infrastructure.persistence.repositories.clickup_repository import SqlAlchemyClickUpRepository

from backend.src.infrastructure.persistence.repositories.repo_repository import SqlAlchemyRepoRepository
from backend.src.infrastructure.persistence.repositories.member_repository import SqlAlchemyMemberRepository


from backend.src.application.services.repo_service import RepoService
from backend.src.application.services.clickup_service import ClickUpService
from backend.src.application.services.associator_service import AssociatorService
from backend.src.application.services.deployment_service import DeploymentService


class Container:
    def __init__(self):
        # DB connector
        self.db = MySQLConnector()

        # Session
        self.session = self.db.get_session()

        # Repositories
        self.repo_repo = SqlAlchemyRepoRepository(self.session)
        self.member_repo = SqlAlchemyMemberRepository(self.session)
        self.clickup_repo = SqlAlchemyClickUpRepository(self.session)

        # External services
        self.github_service = GitHubDeploymentAdapter()

        # Application services
        self.repo_service = RepoService(self.repo_repo)
        self.member_service = MemberService(self.member_repo)
        self.clickup_service = ClickUpService(self.clickup_repo)

        self.associator_service = AssociatorService(
            self.clickup_service,
            self.member_service,
            self.repo_service,
        )

        self.deployment_service = DeploymentService(self.github_service)