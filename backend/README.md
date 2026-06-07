# Backend

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

## Overview
Backend built with FastAPI, SQLAlchemy, MySQL, using layered architecture:
presentation → application → domain → infrastructure.

Supports:
- Auth (JWT)
- ClickUp integration
- AI workflows (backlog, tasks, project status, commits)
- GitHub & deployment analytics

---

## Docs
Full documentation is split into:

- 📐 `docs/ARCHITECTURE.md`
- 📡 `docs/API.md`
- 🤖 `docs/AI_WORKFLOWS.md`

---

## Quick Start

```bash
pip install -r requirements.txt
uvicorn backend.src.presentation.api.main:app --reload
```

---

## Main Dependencies

Key libraries used in this backend:

- **Web**: fastapi, uvicorn, starlette
- **Database**: sqlalchemy, mysql-connector-python
- **Validation**: pydantic
- **Auth**: python-jose, bcrypt
- **HTTP clients**: httpx, requests, aiohttp
- **AI / Azure**: openai, azure-ai-projects, azure-ai-agents, azure-core, azure-identity
- **Scheduling**: apscheduler
- **Templating**: jinja2, pyyaml
- **Testing**: pytest, pytest-asyncio, anyio
- **Config**: python-dotenv

See `requirements.txt` for the complete dependency list.

---

## Tests

```bash
# Run all tests
pytest tests

# Run unit tests only
pytest backend/tests/unit

# Run integration tests only
pytest backend/tests/integration

# Run with coverage
pytest --cov=backend --cov-report=term-missing
```

Current test breakdown:
- Total: 370
- Unit: 310
- Integration: 60

---

## Developer Commands

```bash
# Format code
black .
isort .

# Lint
ruff check .

# Type check
mypy backend
```

---

## CI / Pull Requests

- Create feature branches for changes and open pull requests against `main`.
- Include tests for new functionality and make sure `pytest` passes locally.
- Keep commits and PRs focused on a single change when possible.
- Run unit tests first, then integration tests if external services are available.

---

## Contact
For questions or support, contact: amaidi.shaima@gmail.com