import os
from dotenv import load_dotenv
from pathlib import Path

from backend.src.domain.exceptions.azure.missing_azure_config_exception import MissingAzureConfigException
from backend.src.domain.exceptions.clickup.missing_clickup_config_exception import MissingClickUpConfigException
from backend.src.domain.exceptions.common.missing_env_variable_exception import MissingEnvVariableException
from backend.src.domain.exceptions.database.database_initialization_exception import DatabaseInitializationException


_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_ENV_PATH)


class Settings:

    # --- Cookies et CORS ---
    ALLOW_ORIGINS: list[str] = (os.getenv("ALLOW_ORIGINS") or "").split(",")
    DOMAIN: str | None = os.getenv("DOMAIN") or None

    SECURE: bool = os.getenv("SECURE").lower() == "true"

    # --- MySQL ---
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT"))
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    TOKEN_CLEANUP_INTERVAL_HOURS: int = int(os.getenv("TOKEN_CLEANUP_INTERVAL_HOURS", "24"))

    # --- GitHub ---
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    CONNECT_TIMEOUT: int = int(os.getenv("CONNECT_TIMEOUT", "10"))
    READ_TIMEOUT: int = int(os.getenv("READ_TIMEOUT", "60"))
    ACTIONS_MAX_RUNS: int = int(os.getenv("ACTIONS_MAX_RUNS", "100"))
    DEPLOYMENTS_MAX_ITEMS: int = int(os.getenv("DEPLOYMENTS_MAX_ITEMS", "30"))

    # --- Bing Search ---
    BING_CONNECTION_NAME: str = os.getenv("BING_CONNECTION_NAME")

    # --- Azure OpenAI ---
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # --- Azure Project ---
    AZURE_PROJECT_ENDPOINT: str = os.getenv("AZURE_PROJECT_ENDPOINT")
    AZURE_PROJECT_NAME: str = os.getenv("AZURE_PROJECT_NAME")
    AZURE_SUBSCRIPTION_ID: str = os.getenv("AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP_NAME: str = os.getenv("AZURE_RESOURCE_GROUP_NAME")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET")

    # --- Agents ---
    TASK_CREATOR_AGENT_ID: str = os.getenv("TASK_CREATOR_AGENT_ID")
    TASK_CREATOR_WEB_SEARCH_AGENT_ID: str = os.getenv("TASK_CREATOR_WEB_SEARCH_AGENT_ID")

    # --- Web Search ---
    WEB_SEARCH_MAX_RETRIES: int = int(os.getenv("WEB_SEARCH_MAX_RETRIES", "3"))
    WEB_SEARCH_RETRY_BASE_DELAY: int = int(os.getenv("WEB_SEARCH_RETRY_BASE_DELAY", "2"))
    WEB_SEARCH_RETRY_MAX_DELAY: int = int(os.getenv("WEB_SEARCH_RETRY_MAX_DELAY", "30"))
    WEB_SEARCH_RUN_TIMEOUT: int = int(os.getenv("WEB_SEARCH_RUN_TIMEOUT", "60"))

    # --- ClickUp ---
    CLICKUP_BASE_URL: str = os.getenv("CLICKUP_BASE_URL")
    CLICKUP_TEAM_ID: str = os.getenv("CLICKUP_TEAM_ID")
    CLICKUP_API_TOKEN: str = os.getenv("CLICKUP_API_TOKEN")

    def __init__(self):

        for var in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_DB"]:
            if not getattr(self, var):
                raise DatabaseInitializationException(
                    "The service is not properly configured. Please contact support."
                )

        if not self.JWT_SECRET_KEY:
            raise MissingEnvVariableException()

        if not self.GITHUB_TOKEN:
            raise MissingEnvVariableException()

        if not self.ALLOW_ORIGINS or self.ALLOW_ORIGINS == [""]:
            raise MissingEnvVariableException()

        for var in ["BING_CONNECTION_NAME"]:
            if not getattr(self, var):
                raise MissingAzureConfigException(
                    "The web search service is not properly configured. Please contact your administrator."
                )

        for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME", "AZURE_OPENAI_API_VERSION"]:
            if not getattr(self, var):
                raise MissingEnvVariableException(
                    "The AI service is not properly configured. Please contact your administrator."
                )

        for var in ["AZURE_PROJECT_ENDPOINT", "AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]:
            if not getattr(self, var):
                raise MissingAzureConfigException(
                    "The AI service is not properly configured. Please contact your administrator."
                )

        for var in ["TASK_CREATOR_AGENT_ID", "TASK_CREATOR_WEB_SEARCH_AGENT_ID"]:
            if not getattr(self, var):
                raise MissingAzureConfigException(
                    "The AI service is not properly configured. Please contact your administrator."
                )

        for var in ["CLICKUP_BASE_URL", "CLICKUP_TEAM_ID", "CLICKUP_API_TOKEN"]:
            if not getattr(self, var):
                raise MissingClickUpConfigException(
                    "ClickUp integration is not properly configured. Please contact your administrator."
                )

settings = Settings()