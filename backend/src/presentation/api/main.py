"""FastAPI application factory and configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector
from backend.src.presentation.api.routers import associator_router, clickup_router, repo_router, member_router, deployment_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ClickUp Integration API",
        description="Manage repositories, members, ClickUp spaces and deployments.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 🔹 DB connector (session per request)
    app.state.db = MySQLConnector()

    # 🔹 Routers
    app.include_router(clickup_router.router, prefix="/clickup", tags=["ClickUp"])
    app.include_router(associator_router.router, prefix="/associate", tags=["Associator"])
    app.include_router(repo_router.router, prefix="/repo", tags=["Repo"])
    app.include_router(member_router.router, prefix="/member", tags=["Member"])
    app.include_router(deployment_router.router, prefix="/deployment", tags=["Deployment"])
    return app


app = create_app()