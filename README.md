# DevSync Platform

DevSync Platform is a web application that connects repositories, GitHub activity, ClickUp workspaces, deployments, and AI-assisted project workflows in one interface.

## Capabilities

- JWT authentication and member management
- Repository registration and GitHub integration
- ClickUp spaces, folders, lists, statuses, and tasks
- AI backlog generation with streaming responses
- Meeting-summary and backlog-to-task workflows
- Project status, weekly summaries, and commit traceability
- Deployment and repository activity views

## Repository Layout

```text
devsync_plateform/
|-- backend/       FastAPI application, domain logic, integrations, and tests
|-- frontend/      React/Vite application and generated API client
|-- docs/          Project-wide architecture and operational documentation
`-- docker-compose.yml
```

Component documentation:

- [`backend/README.md`](backend/README.md)
- [`backend/docs/ARCHITECTURE.md`](backend/docs/ARCHITECTURE.md)
- [`backend/docs/API.md`](backend/docs/API.md)
- [`backend/docs/AI_WORKFLOW.md`](backend/docs/AI_WORKFLOW.md)
- [`frontend/README.md`](frontend/README.md)
- [`frontend/docs/ARCHITECTURE.md`](frontend/docs/ARCHITECTURE.md)
- [`frontend/docs/API.md`](frontend/docs/API.md)
- [`frontend/docs/AI_WORKFLOWS.md`](frontend/docs/AI_WORKFLOWS.md)

Project-wide guides:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Architecture Summary

```text
Browser
  |
  v
Frontend (React + Vite)
  |
  v
Backend API (FastAPI)
  |              \
  v               v
MySQL       GitHub / ClickUp / Azure AI
```

The backend owns business rules, persistence, external integrations, and AI orchestration. The frontend owns navigation, user interaction, cache state, error feedback, and stream rendering.

## Local Development

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- MySQL 8 when running the backend without the container stack

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.src.presentation.api.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is available at `/docs` when the backend is running.

## Dockerization

The project is dockerized with a three-service Compose stack:

- `backend`: FastAPI API on port `8000`
- `frontend`: Vite development server on port `5173`
- `mydb`: MySQL 8 on host port `3307`

Start the complete stack from the repository root:

```bash
docker compose up --build
```

Open `http://localhost:5173` for the application and `http://localhost:8000/docs` for the API. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for configuration, logs, lifecycle commands, and data persistence.

## Testing and Quality

```bash
cd backend
pytest tests
pytest --cov=backend --cov-report=term-missing

cd ../frontend
npm run lint
npm run build
```

Keep generated API files synchronized with the backend OpenAPI contract.

## Security Notes

- Keep credentials and API keys in environment files excluded from version control.
- Do not expose backend integration secrets through frontend `VITE_` variables.
- Use HTTPS and secure cookie settings in deployed environments.
- Back up the MySQL volume before destructive maintenance operations.
