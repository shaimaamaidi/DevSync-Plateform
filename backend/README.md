![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-green)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

# Backend


This is the backend service for the project, built with **FastAPI**, **SQLAlchemy**, and **MySQL**. It provides a RESTful API for managing users, repositories, deployments, and integrations with external services.

---


## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
  - [Authentification par Cookies](#authentification-par-cookies)
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


---

### ⚙️ Initialisation du Backend

Avant de lancer le serveur, deux scripts doivent être exécutés pour préparer l'application :

1. **Initialisation de la base de données**
  ```bash
  python scripts/init_db.py
  ```
  Crée les tables et les relations nécessaires.

2. **Création d’un membre admin**
  ```bash
  python scripts/create_admin.py
  ```
  Crée un utilisateur administrateur initial pour pouvoir accéder aux services backend depuis l’extérieur (sécurité).

Ces scripts doivent être exécutés avant de lancer le serveur backend.

---

---

## 🛠️ Project Structure

```
backend/
  src/
    application/      # Business logic and services
    domain/           # Entities, exceptions, ports (interfaces)
    infrastructure/   # DI, persistence, security, external integrations
    presentation/     # API (FastAPI endpoints)
  tests/
    integration/      # Integration tests
    unit/             # Unit tests
```

---

## 📄 API Documentation


Swagger UI: `http://localhost:8000/docs`  
Redoc: `http://localhost:8000/redoc`

---

## 🍪 Authentification par Cookies

Depuis 2026, l'authentification utilise **aussi des cookies HttpOnly/Secure/SameSite** pour le token d'accès JWT :

- Lors de la connexion (`/auth/login`), le backend place le token d'accès dans un cookie sécurisé (HttpOnly, Secure, SameSite=Lax).
- Le frontend n'a pas accès à ce cookie via JavaScript : il est envoyé automatiquement par le navigateur à chaque requête API.
- Le token de rafraîchissement reste géré côté client (stocké en cookie ou localStorage selon l'implémentation frontend).
- Les endpoints protégés vérifient le token d'accès dans le cookie **ou** dans le header `Authorization`.

> **Remarque** : Pour tester les endpoints protégés avec curl ou Postman, il est possible d'utiliser soit le header `Authorization: Bearer <access_token>`, soit d'envoyer le cookie `access_token`.

---

## 🌐 API Endpoints Overview

Below are the main endpoints provided by the backend, with required parameters and return types:

### Deployments
- **GET `/deployments/list`**
  - **Query params:**
    - `repo_url` (string, required): GitHub repository URL
  - **Returns:** `List[DeploymentDTO]`

### Repositories
- **GET `/repo/all`**
  - **Returns:** List of all repositories (`List[GitRepoDTO]`)
- **POST `/repo/`**
  - **Body:** `{ "name": string, "url": string }`
  - **Returns:** Created repository (`GitRepoDTO`)
- **GET `/repo/{id}`**
  - **Path param:** `id` (int, required): Repository ID
  - **Returns:** Repository detail or 404 error


### Auth
- **POST `/auth/login`**
  - **Body:** `{ "username": string, "password": string }`
  - **Returns:** JWT access and refresh tokens
- **POST `/auth/refresh`**
  - **Body:** `{ "refresh_token": string }`
  - **Returns:** New JWT access and refresh tokens
- **GET `/auth/me`**
  - **Header:** `Authorization: Bearer <access_token>`
  - **Returns:** User info for the authenticated user

### Members
### Members
- **GET `/member/all`**
  - **Returns:** List of all members
- **POST `/member/`**
  - **Body:** `{ "username": string, ... }`
  - **Returns:** Created member
  - ⚠️ **Note:** New members can only be added **after logging in** as an authenticated user. Use the Members page in the frontend to manage users.

### ClickUp Integration
- **GET `/clickup/spaces`**
  - **Returns:** List of ClickUp spaces


> **Note:**
> - All endpoints return JSON.
> - For detailed schemas, see the `domain/entities` directory or the OpenAPI docs (`/docs` when running the backend).
> - All endpoints require authentication (JWT Bearer token in the `Authorization` header) **except**:
>   - `/auth/login`
>   - `/auth/refresh`
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
| ALGORITHM                     | JWT algorithm (e.g., HS256)                      | HS256                                |
| ACCESS_TOKEN_EXPIRE_MINUTES   | JWT access token expiration (minutes)            | 30                                   |
| REFRESH_TOKEN_EXPIRE_DAYS     | JWT refresh token expiration (days)              | 7                                    |
| TOKEN_CLEANUP_INTERVAL_HOURS  | Interval for cleaning up expired tokens (hours)  | 24                                   |
| GITHUB_TOKEN                  | GitHub personal access token (for API access)    | <your_github_token>                  |
| CONNECT_TIMEOUT               | GitHub API connect timeout (seconds)             | 10                                   |
| READ_TIMEOUT                  | GitHub API read timeout (seconds)                | 60                                   |
| ACTIONS_MAX_RUNS              | Max GitHub Actions workflow runs to fetch        | 100                                  |
| DEPLOYMENTS_MAX_ITEMS         | Max GitHub deployments to fetch                  | 30                                   |

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

All tests should pass. (Current: **66 tests**)

### 🧪 Test Breakdown

- **Total tests:** 66
- **Unit tests:** 45
- **Integration tests:** 21

---

## 📚 Additional Notes

- All code is type-annotated and tested.
- JWT authentication is implemented using `python-jose`.
- Dependency injection is managed via a `Container` class.
- For any issues, please check the logs or open an issue.

---

## 📞 Contact

For questions or support, contact me at: amaidi.shaima@gmail.com
