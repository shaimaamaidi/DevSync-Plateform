![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.112.0-green)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

# Backend


This is the backend service for the project, built with **FastAPI**, **SQLAlchemy**, and **MySQL**. It provides a RESTful API for managing users, repositories, deployments, and integrations with external services.

The API layer is organized around routers in `src/presentation/api/routers`, while the business rules live in application use cases such as `AuthUseCase`, `DeploymentUseCase`, and `AssociatorUseCase`.

---


## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
  - [Cookie Authentication](#cookie-authentication)
- [Backlog Generation (AI Workflow)](#backlog-generation-ai-workflow)
- [API Endpoints Overview](#api-endpoints-overview)
- [Error Handling / Response Codes](#error-handling--response-codes)
- [Main Dependencies](#main-dependencies)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Additional Notes](#additional-notes)
- [Contact](#contact)

---

## 🚀 Quick Start

1. **Clone the repository** and navigate to the backend directory:
   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **Create and activate a virtual environment:**
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.exemple` to `.env`:
     ```bash
     cp .env.exemple .env  # or copy .env.exemple .env on Windows
     ```
   - Edit `.env` and fill in all required variables (see below).

5. **Run the API server:**
  ```bash
  uvicorn backend.src.presentation.api.main:app --reload
  ```


---

### ⚙️ Backend Initialization

Before starting the server, run these two scripts to prepare the application:

1. **Initialize the database**
  ```bash
  python scripts/init_db.py
  ```
  Creates the required tables and relationships.

2. **Create an admin member**
  ```bash
  python scripts/create_admin.py
  ```
  Creates the initial administrator account used to access backend services securely.

These scripts must be executed before starting the backend server.

---

---

## 🛠️ Project Structure

```
backend/
  src/
    application/      # Application use cases and orchestration
    domain/           # Entities, exceptions, ports (interfaces)
    infrastructure/   # DI, persistence, security, external integrations
    presentation/     # API routers and FastAPI endpoints
  tests/
    integration/      # Integration tests
    unit/             # Unit tests
```

---

## 📄 API Documentation


Swagger UI: `http://localhost:8000/docs`  
Redoc: `http://localhost:8000/redoc`

---

## 🍪 Cookie Authentication

Since 2026, authentication also uses **HttpOnly/Secure/SameSite cookies** for the JWT access token:

- During login (`/auth/login`), the backend stores the access token in a secure cookie (HttpOnly, Secure, SameSite=Lax).
- The frontend cannot access this cookie through JavaScript; the browser sends it automatically with each API request.
- The refresh token remains client-managed (stored in a cookie or localStorage depending on the frontend implementation).
- Protected endpoints validate the access token from the cookie **or** from the `Authorization` header.

> **Note**: To test protected endpoints with curl or Postman, you can either use the `Authorization: Bearer <access_token>` header or send the `access_token` cookie.

---

## 🤖 Backlog Generation (AI Workflow)

The backend includes an AI-driven backlog generation pipeline exposed through **SSE streaming** (`text/event-stream`) via `/backlog/*` routes.

### Purpose

Transform a raw product description into an actionable backlog:
- Epics
- User stories
- Tasks
- Proposed delivery/sprint plan

### Functional Workflow

1. The frontend sends the initial description to `POST /backlog/start`.
2. The backend starts an orchestrated workflow (Azure AI Agent + domain tools) and returns an SSE stream.
3. The workflow generates and validates market intelligence.
4. The backlog is generated (epics/stories/tasks), then can be corrected by the user.
5. The user can iteratively reply through:
  - `POST /backlog/reply` (market-intelligence validation/correction)
  - `POST /backlog/reply/backlog` (backlog validation/correction)

### Backlog Endpoints

- **POST `/backlog/start`**
  - **Body:** `{ "description": string }`
  - **Returns:** SSE stream (`text/event-stream`) with initialization data (`thread_id`) and generated chunks.

- **POST `/backlog/reply`**
  - **Body:** `{ "thread_id": string, "tool_result": string, "user_result": string }`
  - **Returns:** SSE stream continuing the workflow after user feedback on market intelligence.

- **POST `/backlog/reply/backlog`**
  - **Body:** `{ "thread_id": string, "tool_result": string, "user_result": string }`
  - **Returns:** SSE stream with corrected/validated backlog and progression to delivery planning.

### Key Components (Architecture)

- **Use case**: `GenerateBacklogUseCase`
- **Workflow orchestrator**: `BacklogWorkflowOrchestrator`
- **Dedicated DI container**: `BacklogContainer`
- **Domain tools**:
  - `ProductContextBuilderTool`
  - `MarketQueryGeneratorTool`
  - `WebSearchTool`
  - `MarketSummarizerTool`
  - `MarketValidatorTool`
  - `BacklogGeneratorTool`
  - `UserBacklogFixerTool`
  - `DeliveryPlannerTool`

### Important Notes

- Backlog routes are protected by JWT/cookie authentication like other private routes.
- The workflow is designed to be iterative: the same `thread_id` is used to continue a generation session.
- The expected client media type for these endpoints is `text/event-stream`.

---

## 🌐 API Endpoints Overview

Below are the main endpoints provided by the backend, with required parameters and return types:

### Health
- **GET `/health/`**
  - **Returns:** Service health status

### Deployments
- **GET `/deployment/list`**
  - **Query params:**
    - `repo_url` (string, required): GitHub repository URL
  - **Returns:** `List[DeploymentDTO]`

### Authentication
- **POST `/auth/login`**
  - **Body:** `{ "mail": string, "password": string }`
  - **Returns:** JWT access and refresh tokens, and sets the `access_token` cookie
- **POST `/auth/refresh`**
  - **Query param:** `refresh_token` (string, required)
  - **Returns:** New JWT access and refresh tokens, and refreshes the `access_token` cookie
- **POST `/auth/logout`**
  - **Query param:** `refresh_token` (string, required)
  - **Returns:** `true` when the refresh token is revoked

### Associations
- **POST `/associate/space`**
  - **Body:** repository URL + ClickUp space code
  - **Returns:** Updated repository/space association
- **POST `/associate/members`**
  - **Body:** repository URL + complete member list
  - **Returns:** Updated repository members
- **POST `/associate/members/add`**
  - **Body:** repository URL + members to add
  - **Returns:** Updated repository members
- **POST `/associate/members/remove`**
  - **Body:** repository URL + members to remove
  - **Returns:** Updated repository members

### Repositories
- **GET `/repo/all`**
  - **Returns:** List of all repositories (`List[GitRepoDTO]`)
- **GET `/repo/details`**
  - **Returns:** List of repositories with details (`List[GitRepoDetailDTO]`)
- **POST `/repo/`**
  - **Body:** `{ "name": string, "url": string }`
  - **Returns:** Created repository (`GitRepoDTO`)
- **GET `/repo/{id}`**
  - **Path param:** `id` (int, required): Repository ID
  - **Returns:** Repository detail or 404 error
- **GET `/repo/by-name/{name}`**
  - **Path param:** `name` (string, required)
  - **Returns:** Repository detail or 404 error
- **PUT `/repo/{id}`**
  - **Path param:** `id` (int, required)
  - **Body:** repository update payload
  - **Returns:** Updated repository detail
- **DELETE `/repo/{id}`**
  - **Path param:** `id` (int, required)
  - **Returns:** `true` when deletion succeeds

### Members
- **GET `/member/all`**
  - **Returns:** List of all members
- **GET `/member/by-repo/{repo_id}`**
  - **Path param:** `repo_id` (int, required)
  - **Returns:** List of members in that repository (`List[MemberDTO]`)
- **GET `/member/all-with-repos`**
  - **Returns:** List of members with repositories (`List[MemberWithReposDTO]`)
- **POST `/member/`**
  - **Body:** member creation payload (`username`, `mail`, `password`, ...)
  - **Returns:** Created member
- **PUT `/member/{id}`**
  - **Path param:** `id` (int, required)
  - **Body:** member update payload
  - **Returns:** Updated member with repositories
- **DELETE `/member/{id}`**
  - **Path param:** `id` (int, required)
  - **Returns:** `true` when deletion succeeds
  - ⚠️ **Note:** New members can only be added **after logging in** as an authenticated user. Use the Members page in the frontend to manage users.

### ClickUp Integration
- **GET `/clickup/`**
  - **Returns:** List of ClickUp spaces
- **GET `/clickup/light`**
  - **Returns:** List of ClickUp spaces (light view)
- **GET `/clickup/{space_id}`**
  - **Path param:** `space_id` (int, required)
  - **Returns:** ClickUp space details
- **POST `/clickup/`**
  - **Body:** ClickUp space creation payload
  - **Returns:** Created ClickUp space
- **PUT `/clickup/{space_id}`**
  - **Path param:** `space_id` (int, required)
  - **Body:** ClickUp space update payload
  - **Returns:** Updated ClickUp space
- **DELETE `/clickup/{space_id}`**
  - **Path param:** `space_id` (int, required)
  - **Returns:** `true` when deletion succeeds

### ClickUp Task Verification & Save
These endpoints are implemented in dedicated routers and are available when mounted under the `/clickup` prefix in the application factory.

- **POST `/clickup/generate-tasks-from-summary`**
  - **Body:** `{ "meeting_summary": string, "space_id": string }`
  - **Returns:** Generated task list
- **POST `/clickup/verify`**
  - **Body:** `{ "space_id": string, "tasks": [...] }`
  - **Returns:** Verification result with `create` / `update` actions
- **POST `/clickup/save`**
  - **Body:** `{ "space_id": string, "tasks": [...], "ignore_names"?: [...], "ignore_mails"?: [...] }`
  - **Returns:** Save summary (`message`, `total_tasks`)

### Backlog (AI Streaming)
These endpoints are exposed by the backlog router under the `/backlog` prefix.

- **POST `/backlog/start`**
  - **Body:** `{ "description": string }`
  - **Returns:** SSE stream with generated chunks and workflow metadata (`thread_id`)
- **POST `/backlog/reply`**
  - **Body:** `{ "thread_id": string, "tool_result": string, "user_result": string }`
  - **Returns:** SSE stream continuing market-intelligence validation workflow
- **POST `/backlog/reply/backlog`**
  - **Body:** `{ "thread_id": string, "tool_result": string, "user_result": string }`
  - **Returns:** SSE stream for backlog validation/fix and delivery planning continuation


> **Note:**
> - Most endpoints return JSON. The `/backlog/*` routes stream Server-Sent Events (`text/event-stream`).
> - For detailed schemas, see the `domain/entities` directory or the OpenAPI docs (`/docs` when running the backend).
> - All endpoints require authentication (JWT Bearer token in the `Authorization` header) **except**:
>   - `/auth/login`
>   - `/auth/refresh`
>   - `/health/`
>   - `/docs`
>   - `/openapi.json`
>   - `/redoc`
> - To authenticate, include your JWT access token in the `Authorization` header of your requests:
>   - `Authorization: Bearer <your_access_token>`
> - Example with `curl`:
>   ```bash
>   curl -H "Authorization: Bearer <your_access_token>" http://localhost:8000/member/all
>   ```

---

## 🚨 Error Handling / Response Codes

The backend uses standard HTTP status codes for all API responses. Typical codes include:

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input or missing parameters
- **401 Unauthorized**: Authentication required or failed (invalid/missing JWT)
- **403 Forbidden**: Authenticated but not allowed
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource already exists or conflict
- **422 Unprocessable Entity**: Validation error (e.g., FastAPI validation)
- **500 Internal Server Error**: Unexpected server error

> **Error responses** are returned as JSON objects with a standard structure, e.g.:
>
> ```json
> {
>   "error": {
>     "code": "REPO_NOT_FOUND",
>     "message": "Repository not found with ID: 99"
>   }
> }
> ```

---

## 📦 Main Dependencies

Key libraries used in this backend:

- fastapi
- sqlalchemy
- mysql-connector-python
- pydantic
- uvicorn
- python-dotenv
- bcrypt
- apscheduler
- python-jose
- starlette
- httpx
- requests
- pytest
- pytest-asyncio

See `requirements.txt` for the full list.

---

## ⚙️ Environment Variables

All required environment variables are documented in `.env.exemple`. Here are the main variables, their purpose, and example values:

| Variable                      | Description                                      | Example Value                        |
|-------------------------------|--------------------------------------------------|--------------------------------------|
| MYSQL_USER                    | MySQL database username                          | root                                 |
| MYSQL_PASSWORD                | MySQL database password                          | mypassword                           |
| MYSQL_HOST                    | MySQL host address                               | localhost                            |
| MYSQL_PORT                    | MySQL port                                       | 3306                                 |
| MYSQL_DB                      | MySQL database name                              | mydb                                 |
| JWT_SECRET_KEY                | Secret key for JWT signing                       | <random string>                      |
| JWT_ALGORITHM                 | JWT algorithm (e.g., HS256)                      | HS256                                |
| ACCESS_TOKEN_EXPIRE_MINUTES   | JWT access token expiration (minutes)            | 30                                   |
| REFRESH_TOKEN_EXPIRE_DAYS     | JWT refresh token expiration (days)              | 7                                    |
| TOKEN_CLEANUP_INTERVAL_HOURS  | Interval for cleaning up expired tokens (hours)  | 24                                   |
| GITHUB_TOKEN                  | GitHub personal access token (for API access)    | <your_github_token>                  |
| CONNECT_TIMEOUT               | GitHub API connect timeout (seconds)             | 10                                   |
| READ_TIMEOUT                  | GitHub API read timeout (seconds)                | 60                                   |
| ACTIONS_MAX_RUNS              | Max GitHub Actions workflow runs to fetch        | 100                                  |
| DEPLOYMENTS_MAX_ITEMS         | Max GitHub deployments to fetch                  | 30                                   |
| CLICKUP_API_TOKEN             | ClickUp API token used by the ClickUp integration | <your_clickup_api_token>             |

> **Note:**
> - All variables must be set in your `.env` file for the backend to work properly.
> - Some variable names may differ from older versions; always refer to `.env.exemple` for the latest format.
> - Never commit your real secrets or tokens to version control.

See `.env.exemple` for the complete list and details.

---

## 🧪 Running Tests


Run all unit and integration tests:
```bash
pytest tests
```

All tests should pass. (Current: **215 tests**)

### 🧪 Test Breakdown

- **Total tests:** 215
- **Unit tests:** 177
- **Integration tests:** 38

---

## 📚 Additional Notes

- All code is type-annotated and tested.
- JWT authentication is implemented using `python-jose`.
- Dependency injection is managed via a `Container` class.
- Presentation is handled by routers, while business rules are implemented in application use cases.
- For any issues, please check the logs or open an issue.

---

## 📞 Contact

For questions or support, contact me at: amaidi.shaima@gmail.com
