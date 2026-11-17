# Frontend

![React](https://img.shields.io/badge/React-19-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)
![Vite](https://img.shields.io/badge/Vite-8-purple)

## Overview

The frontend is a React single-page application for repository, ClickUp, deployment, and project-insight workflows.

It provides:

- JWT session management with automatic refresh
- Repository, member, and deployment views
- ClickUp space, list, status, and task management
- AI-assisted backlog, meeting-task, and project-insight workflows
- Server-Sent Events for interactive backlog generation
- Consistent loading, error, retry, and network-status feedback

## Docs

Full documentation is split into:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/API.md`](docs/API.md)
- [`docs/AI_WORKFLOWS.md`](docs/AI_WORKFLOWS.md)

## Quick Start

Requirements: Node.js 20 or newer and npm.

```bash
npm install
npm run dev
```

The development server is available at `http://localhost:5173`.

## Configuration

Create `frontend/.env.local` with:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_REFRESH_TOKEN_EXPIRE_DAYS=7
```

`VITE_API_BASE_URL` must point to the backend API base URL. Values prefixed with `VITE_` are exposed to the browser, so do not put secrets in this file.

## Main Dependencies

- **UI**: React, Tailwind CSS, Radix UI, Lucide React
- **Routing**: React Router
- **Server state**: TanStack React Query
- **HTTP**: Axios and the generated TypeScript API client
- **Forms and feedback**: React Hook Form, Sonner, React Toastify
- **Charts**: Recharts
- **Tooling**: Vite, TypeScript, ESLint

## Commands

```bash
# Start the development server
npm run dev

# Build for production
npm run build

# Run lint checks
npm run lint

# Preview a production build
npm run preview

# Regenerate the API client from the backend OpenAPI document
npm run generate:api
```

## API Client

Files under `src/api` are generated from the backend OpenAPI document. Use services under `src/services` and hooks under `src/hooks` from application code; do not manually edit generated API classes.

## Project Structure

```text
src/
├── api/          Generated API client and Axios configuration
├── components/   Shared layout, navigation, and UI components
├── hooks/        React Query and workflow hooks grouped by domain
├── lib/          Mappers, guards, and domain helpers
├── pages/        Route-level screens
├── services/     API orchestration and session services
├── types/        Frontend-specific TypeScript types
└── utils/        Error handling and stream parsing helpers
```

## Development Guidelines

- Keep route-level composition in `src/pages` and reusable behavior in hooks or services.
- Keep generated API files synchronized with the backend contract.
- Handle authenticated requests through the shared API configuration and session service.
- Add loading, empty, error, and retry states to user-facing data flows.
- Run `npm run lint` and `npm run build` before opening a pull request.