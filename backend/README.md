# Backend

Backend service for the ClickUp integration platform. It provides FastAPI endpoints to manage Git repositories, members, ClickUp spaces, and deployment data.

## Features
- Repository CRUD and association with ClickUp spaces and members
- Member management with repository links
- ClickUp space management
- GitHub deployments listing
- Centralized exception handling and structured logging

## Tech Stack
- Python 3.12+
- FastAPI
- SQLAlchemy
- MySQL (mysql-connector-python)
- Pydantic
- Pytest (tests)

## Project Structure
- src/application: application services
- src/domain: entities, ports, and exceptions
- src/infrastructure: persistence, external adapters, logging, and DI container
- src/presentation: API layer (FastAPI routers, middleware, deps)
- tests: unit and integration tests

## Environment Variables
Create a local .env file in backend/ (see .env.exemple):
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_HOST
- MYSQL_PORT
- MYSQL_DB

## Setup
From the repository root:

1) Create and activate a virtual environment (example):
- Windows PowerShell:
  - python -m venv backend/.venv
  - backend/.venv/Scripts/Activate.ps1

2) Install dependencies:
- python -m pip install -r backend/requirements.txt

## Run the API
From the repository root:
- uvicorn backend.src.presentation.api.main:app --reload

The API will be available at http://127.0.0.1:8000

## Initialize the Database
This creates the database and tables (requires valid env vars):
- python -m backend.src.infrastructure.scripts.init_db

## Run Tests
From the repository root:
- python -m pytest backend/tests

Current test count:
- Total: 49
- Unit: 29
- Integration: 20

## Notes
- The API uses request id middleware to add X-Request-Id headers and log correlation.
- Exception handlers map domain errors to consistent JSON responses.
