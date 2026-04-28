
![Node.js](https://img.shields.io/badge/node-%3E=18.0.0-brightgreen)
![Vite](https://img.shields.io/badge/vite-5.x-blue)
![React](https://img.shields.io/badge/react-18.x-blue)

# Frontend

This is the frontend for the platform, built with **React**, **TypeScript**, **Vite**, and **Tailwind CSS**. It consumes the backend API for managing members, repositories, deployments, and ClickUp integrations.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
   - [Authentication with Cookies](#authentication-with-cookies)
- [API Client & Auth](#api-client--auth)
---

## 📄 API Documentation

The frontend consumes the backend REST API documented at:

- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

---

## 🍪 Authentication & Cookies

The frontend uses cookies to manage authentication:

- On login (`/auth/login`), the backend sets the access token (JWT) in a secure cookie (`HttpOnly`, `Secure`, `SameSite=Lax`).
- This cookie is automatically sent by the browser with each API request and is not accessible from JavaScript.
- The refresh token is managed client-side (cookie or localStorage).
- Protected endpoints validate the access token either from the cookie or from the `Authorization` header.
- No primary authentication data is stored in localStorage.

> Note: To test protected endpoints with curl or Postman, you can either send an `Authorization: Bearer <access_token>` header or include the `access_token` cookie.
- [Main Features](#main-features)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Main Dependencies](#main-dependencies)
- [Additional Notes](#additional-notes)
- [Contact](#contact)

---

## 🚀 Quick Start

1. **Clone the repository and go to the frontend folder:**
   ```bash
   git clone <repo-url>
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   - Copy `.env.example` in `.env`.
   - Edit variables in `.env` (see dedicated section).
   - Copy `openapitools.json` **only if you need to regenerate the API client** (see below).

4. **Generate the API client (if backend changed):**
   ```bash
   npm run generate:api
   ```

5. **Start the development server:**
   ```bash
   npm run dev
   ```

---

## 🛠️ Project Structure

```
frontend/
  src/
    api/           # Generated API client (OpenAPI)
    components/    # React components (UI, tables, modals...)
    hooks/         # Custom React hooks
    lib/           # Utility functions
    pages/         # Main pages (Home, NotFound...)
    services/      # Business logic services (auth, members, repos...)
    assets/        # Images, logos, etc.
    App.tsx        # Main entry point
    main.tsx       # React bootstrap
  public/          # Static files
  index.html       # Main HTML
  package.json     # Dependencies and scripts
  vite.config.ts   # Vite config
  tailwind.config.js # Tailwind config
```

---

## 🔐 API Client & Auth

- **API client** is auto-generated from the backend (OpenAPI): see `src/api/` and `src/apiClient.ts`.
- **Authentication**:
  - Uses JWT in HttpOnly/Secure/SameSite cookie for the access token (handled automatically by the browser).
  - The refresh token is stored client-side (cookie or localStorage).
  - Axios interceptor automatically refreshes the access token on 401 errors.
  - Frontend routes are protected based on authentication state.

---

## ✨ Main Features

- Member management (login, edit)
   - ⚠️ New members must be created via the Members page after logging in with an existing admin account.
- GitHub repository management
- Deployment tracking
- ClickUp integration (spaces, associations)
- Modern, responsive UI (Tailwind CSS)
- Global error and success notifications
- Agent de génération de backlog: Génération automatisée de tickets/éléments
 - ClickUp integration (spaces, associations)
 - Modern, responsive UI (Tailwind CSS)
 - Global error and success notifications
 - Backlog generation agent: automated generation of backlog items (stories, tasks, bugs) from product context using an integrated agent. The agent can be triggered from the Backlog UI and communicates with the backend API to create and suggest backlog entries ready for editing.

---

## ⚙️ Environment Variables

Create a `.env` file at the root of the frontend if needed. Main variables:

| Variable           | Description                        | Example                |
|--------------------|------------------------------------|------------------------|
| VITE_API_BASE_URL  | Backend API URL                    | http://localhost:8000  |
| VITE_REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiration (days) | 7 |

---


## 📦 Main Dependencies

- react
- react-dom
- typescript
- vite
- tailwindcss
- axios
- @tanstack/react-query
- openapi-typescript-codegen
- @radix-ui/react-* (UI components)
- lucide-react (icons)
- react-toastify (notifications)

See `package.json` for the full list.

---

## 🎨 UI/UX

- Modern, responsive interface built with Tailwind CSS
- Advanced UI components via Radix UI (`@radix-ui/react-*`)
- Icons provided by Lucide
- Global notifications (success/error) with React Toastify

---

## 🛡️ Error Handling

- API errors are displayed through a single global toaster using `react-toastify`.
- The `ToastContainer` is mounted once at the application root in `src/main.tsx`.
- Use the helper functions exported from `src/components/global-toaster.tsx`:
   - `showErrorToast(message, title?)` — show an error toast.
   - `showSuccessToast(message, title?)` — show a success toast.
- Hooks and services handle errors and use these helpers. For example, the backlog chat hook `src/hooks/use-chat-logic.ts` handles `SseError` and calls `showErrorToast` for backend/server errors; authentication errors trigger logout/redirect and surface an error toast.

Notes:
- The project uses one global toast container; individual components should call the exported helper functions rather than mounting their own `ToastContainer` instances.
---


## 🧭 Backlog Generation Agent

The project implements an integrated Backlog Generation Agent that creates structured backlog items (epics, user stories, tasks) from a product description and market intelligence. Implementation notes and where to look:

- Purpose: generate and refine backlog items automatically and stream results to the UI for progressive display and user validation.
- Backend endpoints (streaming / SSE):
   - `POST /backlog/start` — start a new generation stream
   - `POST /backlog/reply` — submit market-intelligence verification replies
   - `POST /backlog/reply/backlog` — submit backlog refinement replies
- Frontend service (SSE client): `src/services/backlog-generation-service.ts`
   - Exposes `start()`, `reply()`, and `replyBacklog()` which return `ReadableStream<Uint8Array>` and handle SSE errors.
- SSE parser: `src/utils/stream-parser.ts` (used to read Server-Sent Events and emit chunks to the UI).
- UI integration:
   - `src/components/backlog-generation-chat.tsx` — chat-like UI which renders the conversation and streaming text.
   - `src/hooks/use-chat-logic.ts` — central hook managing messages, streaming state, calls to the backlog service, error handling, and actions (send, reply, submit backlog). This hook calls `readSseStream`, updates message streaming, and uses `showErrorToast` on errors.
   - `src/pages/Home.tsx` — mounts the backlog chat when `activeTab === 'backlog-generation'`.
- Error handling in the flow: `use-chat-logic` catches `SseError` and other runtime errors, uses `showErrorToast`, performs logout + redirect on auth errors, and ensures user-facing messages are shown when a stream fails.

Recommended places to review or extend the feature:
- Start: `src/hooks/use-chat-logic.ts` (logic and SSE integration).
- UI: `src/components/backlog-generation-chat.tsx` and related `Chat*` subcomponents.
- Service: `src/services/backlog-generation-service.ts` (network & SSE helpers).
- Backend workflow/orchestrator: `backend/src/application/use_cases/generate_backlog_use_case.py`, `backlog_router.py`, and the orchestrator/tool/agent classes under `backend/src/infrastructure/external/backlog_generation/`.

---

## 📚 Additional Notes

- The code is fully typed with TypeScript and follows modern React best practices.
- The API client must be regenerated (`npm run generate:api`) after any backend change.

---

## 📞 Contact

For any questions or support, contact: amaidi.shaima@gmail.com
