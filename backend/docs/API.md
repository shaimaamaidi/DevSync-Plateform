# API Reference

## Authentication
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- Header: Authorization: Bearer <token>

---

## Core Modules

### Repositories
- GET /repo/all
- GET /repo/{id}
- POST /repo/
- PUT /repo/{id}
- DELETE /repo/{id}

---

### Members
- GET /member/all
- POST /member/
- GET /member/by-repo/{repo_id}

---

### ClickUp Structure
- POST /clickup/structure/spaces
- POST /clickup/structure/folders
- POST /clickup/structure/lists
- POST /clickup/structure/lists/{list_id}/statuses

---

### ClickUp Tasks

#### Summary Flow
- POST /clickup/tasks/generate-tasks-from-summary
- POST /clickup/tasks/verify-from-summary
- POST /clickup/tasks/save-summary-tasks

#### Backlog Flow
- POST /clickup/tasks/generate-tasks-from-backlog
- POST /clickup/tasks/verify-from-backlog
- POST /clickup/tasks/save-backlog-tasks

---

## AI Endpoints

### Backlog (SSE)
- POST /backlog/start
- POST /backlog/reply
- POST /backlog/reply/backlog

---

### Task Status
- POST /task-status/search
- POST /task-status/synthesize

---

### Project Status
- POST /project-status/status

---

### Weekly Summary
- POST /weekly-summary/summary

---

### Commit Traceability
- POST /commit-traceability/find-task-by-commit

---

## Error Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```