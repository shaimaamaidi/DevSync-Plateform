# Deployment and Dockerization

## 1. Dockerization Announcement

DevSync Platform is dockerized as a complete three-service application. The Compose configuration builds the backend and frontend images and starts a MySQL 8 database with a persistent named volume.

## 2. Services

| Service | Image/build | Host port | Purpose |
|---|---|---:|---|
| `backend` | `backend/Dockerfile` | `8000` | FastAPI API and application workflows |
| `frontend` | `frontend/Dockerfile` | `5173` | React/Vite user interface |
| `mydb` | MySQL 8.0 image | `3307` | Application database |

The services share the `devsync_net` network. The backend reaches the database at the service hostname `mydb` and container port `3306`.

## 3. Required Configuration

Before starting the stack, provide the environment files expected by Compose:

- `backend/.env` for backend and integration settings
- `frontend/.env` for browser-exposed Vite settings
- a root environment file for the MySQL values referenced by `docker-compose.yml`

Frontend example:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_REFRESH_TOKEN_EXPIRE_DAYS=7
```

The root database settings must include values equivalent to:

```env
MYSQL_ROOT_PASSWORD=change-me
MYSQL_DB=devsync
MYSQL_USER=devsync
MYSQL_PASSWORD=change-me
```

Use real secrets only in local untracked files or a deployment secret manager. Never commit them.

## 4. Start and Stop

From the repository root:

```bash
docker compose up --build
```

Run in the background:

```bash
docker compose up --build -d
```

Stop services without deleting database data:

```bash
docker compose down
```

Inspect status and logs:

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mydb
```

## 5. Initialization

The backend service initializes the database and creates the administrator before starting Uvicorn. The database health check must pass before backend startup proceeds.

The frontend is served by the Vite development command inside its container and is exposed on port `5173`.

## 6. Persistence and Reset

MySQL data is stored in the named volume `mysql_data` and remains available after `docker compose down`.

To remove the database volume and recreate the database from scratch:

```bash
docker compose down -v
docker compose up --build
```

This permanently deletes the local database volume. Back up required data first.

## 7. Health Checks

- Frontend: open `http://localhost:5173`
- Backend API: open `http://localhost:8000/health`
- Backend OpenAPI: open `http://localhost:8000/docs`
- Database: inspect `docker compose ps` and the `mydb` health status

## 8. Production Considerations

- Replace development server commands with production-serving processes.
- Build the frontend with a deployment-specific `VITE_API_BASE_URL`.
- Store secrets outside the repository.
- Use HTTPS and secure cookie configuration.
- Restrict exposed database ports when external database access is not required.
- Configure backups, log retention, resource limits, and health monitoring.
