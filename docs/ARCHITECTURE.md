# Project Architecture

## 1. System Overview

DevSync Platform follows a client-server architecture:

```text
React frontend -> FastAPI backend -> MySQL
                         |
                         +-> GitHub API
                         +-> ClickUp API
                         +-> Azure AI services
```

The frontend is a browser application. The backend is the system boundary for authentication, business rules, persistence, third-party APIs, scheduling, and AI workflows.

## 2. Backend Boundary

The backend uses layered architecture:

- **Presentation**: FastAPI application, routers, DTOs, middleware, and exception handlers
- **Application**: use cases and workflow orchestration
- **Domain**: entities, ports, rules, and domain exceptions
- **Infrastructure**: repositories, external clients, security, configuration, scheduling, and dependency injection

The domain layer remains independent from framework and integration details. Use cases depend on ports and are wired through infrastructure containers.

## 3. Frontend Boundary

The frontend uses a domain-oriented React structure:

- **Pages** compose route-level experiences.
- **Components** provide reusable UI, forms, tables, chat panels, and task controls.
- **Hooks** manage React Query state, mutations, and local workflow state.
- **Services** isolate API calls, authentication, streaming, and domain transformations.
- **Generated client** provides OpenAPI request methods and DTOs.
- **Utilities** normalize errors, parse streams, map backlog data, and validate shapes.

`RequireAuth` protects the application shell, while `RequireAdminRoute` protects member administration.

## 4. Request Lifecycle

Normal API call:

```text
Page -> Hook -> Service -> Generated Axios client -> Backend router -> Use case -> Adapter
```

Streaming AI call:

```text
Chat page -> Chat hook -> Streaming service -> fetch/SSE -> Stream parser -> Incremental UI state
```

The frontend keeps API details out of page components. The backend keeps external provider details out of domain rules.

## 5. Authentication

The frontend stores the refresh token in a cookie and uses the shared Axios interceptor for session recovery. The backend validates access tokens through its authentication middleware and exposes login, refresh, logout, and current-user endpoints.

Concurrent `401` responses share one refresh operation. Waiting requests are replayed after a successful refresh; failed refreshes clear the session and redirect the user to login.

## 6. Data and Integration Flow

- MySQL stores application data and project relationships.
- GitHub supplies repositories, commits, actions, and deployment-related activity.
- ClickUp supplies spaces, members, task structure, and task state.
- Azure AI services support backlog, task, status, and summary workflows.
- Server-Sent Events carry incremental backlog workflow output to the frontend.

## 7. Container Topology

The Compose stack runs three services on one private application network:

```text
frontend:5173 -> backend:8000 -> mydb:3306
                         |
                         +-> External integrations
```

The database uses a named volume so data survives service recreation. Host port `3307` maps to the database container port `3306`.

## 8. Design Goals

- clear ownership between browser, API, domain, and infrastructure
- testable use cases and isolated integrations
- generated contract alignment between backend and frontend
- resilient authentication and error handling
- observable, incremental AI workflows
- reproducible local and containerized environments
