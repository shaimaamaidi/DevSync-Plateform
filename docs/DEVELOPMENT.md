# Development Guide

## 1. Start with the Right Component

Use the backend for business logic, persistence, integrations, authentication, and AI orchestration. Use the frontend for presentation, interaction, cache state, stream rendering, and user feedback.

Avoid placing business rules in React components or HTTP-specific logic in domain entities.

## 2. Backend Workflow

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.src.presentation.api.main:app --reload
```

Run checks:

```bash
pytest tests
pytest tests/unit
pytest tests/integration
pytest --cov=backend --cov-report=term-missing
ruff check .
black .
isort .
mypy backend
```

Backend environment variables are documented by the backend architecture guide and should be supplied through a local environment file.

## 3. Frontend Workflow

```bash
cd frontend
npm install
npm run dev
```

Run checks:

```bash
npm run lint
npm run build
npm run preview
```

The frontend requires:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 4. API Client Updates

The frontend API client is generated from the backend OpenAPI document. After a backend contract change:

1. Start the backend so `/openapi.json` is available.
2. Run `npm run generate:api` from `frontend`.
3. Review generated types and methods.
4. Update the relevant service, hook, page, and documentation.
5. Run `npm run lint` and `npm run build`.

Do not manually edit generated classes under `frontend/src/api`.

## 5. Feature Checklist

- Define or update the backend DTO and route.
- Add or update backend use-case and integration tests.
- Regenerate the frontend API client.
- Add a frontend service method and a domain hook when server state is involved.
- Cover loading, empty, success, validation, network, and authentication states.
- Update the relevant component and project documentation.

## 6. Pull Requests

- Keep changes focused on one feature or fix.
- Include tests for new backend behavior.
- Keep generated API changes tied to the contract change that caused them.
- Describe environment or migration requirements.
- Run the relevant checks locally before review.
