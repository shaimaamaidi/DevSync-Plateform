
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

L’application frontend utilise les **cookies** pour la gestion de l’authentification :

- À la connexion (`/auth/login`), le backend place le token d’accès (JWT) dans un cookie sécurisé (**HttpOnly**, **Secure**, **SameSite=Lax**).
- Ce cookie est automatiquement envoyé par le navigateur à chaque requête API (le frontend n’y a pas accès en JavaScript).
- Le refresh token est géré côté client (cookie ou localStorage).
- Les endpoints protégés vérifient le token d’accès dans le cookie **ou** dans l’en-tête `Authorization`.
- **Aucune donnée d’authentification n’est stockée dans le localStorage pour l’accès principal.**

> **Note :** Pour tester les endpoints protégés avec curl ou Postman, vous pouvez utiliser soit l’en-tête `Authorization: Bearer <access_token>`, soit envoyer le cookie `access_token`.
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

- Interface moderne et responsive avec Tailwind CSS
- Composants UI avancés via Radix UI (`@radix-ui/react-*`)
- Icônes via Lucide
- Notifications globales (succès/erreur) avec React Toastify

---

## 🛡️ Gestion des erreurs

- Les erreurs API sont capturées et affichées via des toasts (voir `src/services/api-error.ts` et les composants `global-success-toaster.tsx`/`global-error-toaster.tsx`).
- Les erreurs d’authentification déclenchent un rafraîchissement automatique du token ou une redirection vers la page de login.

---

## 📚 Additional Notes

- The code is fully typed with TypeScript and follows modern React best practices.
- The API client must be regenerated (`npm run generate:api`) after any backend change.

---

## 📞 Contact

For any questions or support, contact: amaidi.shaima@gmail.com
