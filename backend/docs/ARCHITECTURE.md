# Architecture

## Overview
This backend follows a **layered architecture** designed for scalability, testability, and clear separation of concerns.

Layers:
- **Presentation Layer** → FastAPI routers, request/response DTOs
- **Application Layer** → Use cases (business orchestration)
- **Domain Layer** → Entities, ports, business rules
- **Infrastructure Layer** → DB, external APIs, security, DI

---

## 1. Design Principles

### Separation of Concerns
Each layer has a strict responsibility:
- Presentation → HTTP only
- Application → orchestration
- Domain → business logic
- Infrastructure → external systems

---

### Thin Controllers
FastAPI routers:
- validate input (Pydantic)
- call use cases
- return DTOs

No business logic in controllers.

---

### Use Case Driven Architecture
All business logic is implemented in **use cases**:
- independent of FastAPI
- independent of DB
- fully unit-testable

---

## 2. Dependency Injection
DI is handled via **explicit containers**:

Examples:
- `BacklogContainer`
- `ClickUpContainer`
- `TaskGenerationContainer`

Each container is responsible for:
- repositories
- external clients
- AI agents/tools
- configuration wiring

Benefits:
- testability
- isolation
- clear dependency graph

---

## 3. Domain Layer
Contains:
- Entities (core models)
- Ports (interfaces)
- Domain rules
- Exceptions

No external dependency allowed.

---

## 4. Application Layer
Contains:
- Use cases
- Orchestration logic
- Workflow coordination
- DTO transformation

Example responsibilities:
- generate tasks
- verify tasks
- map commits
- summarize projects

---

## 5. Infrastructure Layer
Responsible for external systems:
- MySQL (SQLAlchemy repositories)
- ClickUp API
- GitHub API
- Azure OpenAI
- Web search (Bing / Azure)
- Authentication (JWT)
- Scheduling (APScheduler)

---

### Environment Variables

All required variables are documented in `.env.exemple`. Main variables include:

| Category | Variables |
|---|---|
| **MySQL** | `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB` |
| **JWT** | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` |
| **Cleanup** | `TOKEN_CLEANUP_INTERVAL_HOURS` |
| **GitHub** | `GITHUB_TOKEN`, `CONNECT_TIMEOUT`, `READ_TIMEOUT`, `ACTIONS_MAX_RUNS`, `DEPLOYMENTS_MAX_ITEMS` |
| **ClickUp** | `CLICKUP_API_TOKEN`, `CLICKUP_TEAM_ID` |
| **Azure OpenAI** | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_DEPLOYMENT_NAME` |
| **Azure / Web Search** | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_PROJECT_ENDPOINT`, `BING_CONNECTION_NAME`, `WEB_SEARCH_MAX_RETRIES`, `WEB_SEARCH_RETRY_BASE_DELAY`, `WEB_SEARCH_RETRY_MAX_DELAY`, `WEB_SEARCH_RUN_TIMEOUT` |

---

## 6. AI Architecture
AI system is structured into 3 components:

### 1. Agents
Responsible for reasoning using LLMs.

Examples:
- Task generator agents
- Verifier agents
- Commit mapper agents

---

### 2. Tools
Reusable capabilities:
- web search
- summarization
- validation
- context building

---

### 3. Orchestrators
Control workflow execution:
- `BacklogWorkflowOrchestrator`
- Task generation pipelines

---

## 7. Streaming Architecture (SSE)
Used in `/backlog`:
- Server-Sent Events (`text/event-stream`)
- incremental reasoning output
- real-time AI interaction
- session-based via `thread_id`

---

## 8. Folder Structure

```text
src/
├── presentation/
├── application/
├── domain/
└── infrastructure/
```

---

## 9. Key Design Goals

- scalability
- testability
- modular AI workflows
- clean separation of concerns
- extensible integrations