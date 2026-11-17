# Frontend AI Workflows

The frontend provides the interaction layer for AI workflows exposed by the backend. It handles form state, stream consumption, task review, verification, and persistence.

## 1. Backlog Generation Chat

### Goal

Guide a user through product discovery and produce a structured sprint backlog.

### Flow

1. `BacklogGenerationChatPage` collects the product input.
2. `useChatLogic` starts or replies to the workflow.
3. `backlog-generation-service.ts` sends authenticated streaming requests.
4. `stream-parser.ts` converts SSE chunks into chat events.
5. The page displays progress, questions, backlog content, and delivery planning results.

### Endpoints

- `POST /backlog/start`
- `POST /backlog/reply`
- `POST /backlog/reply/backlog`
- `POST /backlog/delivery-plan`

The stream supports session continuity through the workflow thread identifier.

## 2. Meeting Summary to ClickUp Tasks

### Goal

Transform meeting notes into actionable ClickUp tasks.

### Flow

1. `MeetingTaskGenerationPage` accepts a meeting summary and space.
2. `task-generation-service.ts` requests generated tasks.
3. The user reviews and verifies the proposed tasks.
4. `save-in-clickup-service.ts` persists approved tasks.

### Endpoints

- `POST /clickup/tasks/generate-tasks-from-summary`
- `POST /clickup/tasks/verify-from-summary`
- `POST /clickup/tasks/save-summary-tasks`

## 3. Backlog to ClickUp Tasks

### Goal

Convert selected sprint backlog items into ClickUp tasks.

### Flow

1. `BacklogTaskGenerationPage` loads or receives sprint backlog data.
2. The user clicks **Generate tasks** for the selected ClickUp space.
3. When the ClickUp structure is empty, `map_sprint_backlog_to_tasks` maps the backlog directly in the frontend.
4. When ClickUp structure metadata is available, the page calls `POST /clickup/tasks/generate-tasks-from-backlog` for backend task generation.
5. The user reviews and verifies the result.
6. Approved tasks are saved in ClickUp.

### Endpoints

- `POST /clickup/tasks/generate-tasks-from-backlog`
- `POST /clickup/tasks/verify-from-backlog`
- `POST /clickup/tasks/save-backlog-tasks`

The frontend mapper is the generation path for spaces without folders or lists. The first endpoint is a manual, conditional backend path, not an automatic request made when the page loads.

## 4. Project Insights

`ProjectInsightsPage` groups three conversational project-analysis workflows:

- **Task status**: natural-language task search and status synthesis
- **Project status**: project health and activity overview
- **Weekly summary**: a narrative report from recent project activity

The UI uses `project-tracking-service.ts` and exposes:

- `POST /task-status/search`
- `POST /task-status/synthesize`
- `POST /project-status/status`
- `POST /weekly-summary/summary`

## 5. Commit Traceability

The project insights experience can map a GitHub commit to a ClickUp task through:

- `POST /commit-traceability/find-task-by-commit`

The result is presented as a match, no match, or an empty ClickUp result.

## 6. Frontend Workflow Principles

- keep generated results editable before persistence
- show progress while asynchronous work is running
- preserve stream and chat state across incremental events
- make retry and authentication expiry visible to the user
- invalidate affected React Query data after successful mutations
- keep backend DTO details inside services and workflow hooks