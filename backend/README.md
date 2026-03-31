
# Backend

This is the backend service for the project, built with **FastAPI**, **SQLAlchemy**, and **MySQL**. It provides a RESTful API for managing users, repositories, deployments, and integrations with external services.

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

5. **Run the application:**
   ```bash
   uvicorn src.presentation.api.main:app --reload
   ```

---

## 🧪 Running Tests


Run all unit and integration tests:
```bash
pytest tests
```

All tests should pass. (Current: **65 tests**)

### 🧪 Test Breakdown

- **Total tests:** 65
- **Unit tests:** 45
- **Integration tests:** 20

---

## 📦 Main Dependencies

Key libraries used in this backend:

- fastapi
- sqlalchemy
- mysql-connector-python
- pydantic
- uvicorn
- python-dotenv
- passlib
- apscheduler
- python-jose
- starlette
- httpx
- requests
- pytest

See `requirements.txt` for the full list.

---

## ⚙️ Environment Variables

All required environment variables are documented in `.env.exemple`. Key variables include:

| Variable                | Description                                 |
|-------------------------|---------------------------------------------|
| DB_HOST                 | Database host                               |
| DB_PORT                 | Database port                               |
| DB_USER                 | Database username                           |
| DB_PASSWORD             | Database password                           |
| DB_NAME                 | Database name                               |
| SECRET_KEY              | Secret key for JWT                          |
| JWT_ALGORITHM           | Algorithm for JWT (e.g., HS256)             |
| ACCESS_TOKEN_EXPIRE_MIN | Access token expiration (minutes)           |
| REFRESH_TOKEN_EXPIRE_MIN| Refresh token expiration (minutes)          |
| CLICKUP_CLIENT_ID       | ClickUp API client ID                       |
| CLICKUP_CLIENT_SECRET   | ClickUp API client secret                   |
| GITHUB_CLIENT_ID        | GitHub OAuth client ID                      |
| GITHUB_CLIENT_SECRET    | GitHub OAuth client secret                  |

See `.env.exemple` for the complete list and details.

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

## 📚 Additional Notes

- All code is type-annotated and tested.
- JWT authentication is implemented using `python-jose`.
- Dependency injection is managed via a `Container` class.
- For any issues, please check the logs or open an issue.

---

## 📞 Contact

For questions or support, contact me at: amaidi.shaima@gmail.com
