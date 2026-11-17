# Frontend Architecture

## Overview

The frontend is a Vite-powered React single-page application. It is organized around route-level pages, reusable components, domain hooks, service modules, and a generated API client.

## 1. Application Layers

- **Application shell**: `App.tsx`, routing, authentication guards, layout, and global notifications
- **Pages**: route-level screens that compose domain components
- **Components**: reusable layout, tables, forms, chats, and task controls
- **Hooks**: React Query data access, mutations, local workflow state, and responsive behavior
- **Services**: API calls, authentication, SSE requests, and domain orchestration
- **API client**: generated Axios classes and request models under `src/api`
- **Utilities**: error normalization, stream parsing, guards, and data mappers

## 2. Routing and Access Control

`src/App.tsx` defines the browser routes.

- `RequireAuth` protects the authenticated application shell.
- `RequireAdminRoute` additionally protects member administration.
- `RootLayout` provides navigation and the shared page frame.
- `/login` remains public.
- Unknown routes render `NotFoundPage`.

The root route redirects to `/repositories`.

## 3. Data Flow

The standard request path is:

```text
Page → Hook → Service → Generated API class → Backend API
                  ↓
             Query cache / UI state
```

TanStack React Query manages server state, cache invalidation, loading states, and mutations. Services translate UI-friendly arguments into generated request DTOs.

## 4. Authentication and HTTP Errors

`auth-service.ts` stores the refresh token in a browser cookie and exposes login, logout, refresh, and current-user operations.

The shared Axios interceptor:

- retries requests after a successful `401` refresh
- queues concurrent requests during one refresh operation
- retries safe idempotent requests according to error policies
- detects network loss and broadcasts network state
- emits normalized application error events for global feedback

SSE requests use the backlog service, which implements equivalent refresh-and-retry behavior for `fetch` streams.

## 5. Generated API Boundary

The generated client in `src/api` is derived from OpenAPI. Domain code should call it through `src/services` rather than coupling components directly to generated method names. Regenerate the client when the backend contract changes.

## 6. Folder Structure

```text
src/
├── api/
├── components/
├── hooks/
├── lib/
├── pages/
├── services/
├── types/
└── utils/
```

## 7. Design Goals

- predictable route and access-control behavior
- isolated domain API logic
- cache-aware asynchronous workflows
- resilient authentication and network handling
- reusable UI primitives with explicit loading and error states
- generated contract alignment with the backend