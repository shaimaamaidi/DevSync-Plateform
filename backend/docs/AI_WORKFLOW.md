# AI Workflows

This document describes all AI-driven workflows in the backend.

All workflows follow:

Input → Orchestrator → Tools → Agents → Structured Output

---

# 1. Backlog Generation (SSE Workflow)

## Goal
Transform a raw product description into a structured backlog.

---

## Flow

1. POST `/backlog/start`
2. Streaming via SSE (`text/event-stream`)
3. Product context extraction
4. Market research (web search)
5. Market validation
6. Backlog generation
7. Delivery planning
8. User feedback loop

---

## Key Features

- real-time streaming
- iterative refinement
- conversational loop
- session-based (`thread_id`)

---

## Core Components

- BacklogWorkflowOrchestrator
- ProductContextBuilderTool
- MarketQueryGeneratorTool
- WebSearchTool
- MarketSummarizerTool
- MarketValidatorTool
- BacklogGeneratorTool
- UserBacklogFixerTool
- DeliveryPlannerTool

---

# 2. ClickUp Tasks — Summary Flow

## Goal
Convert meeting notes → ClickUp tasks

---

## Flow

1. POST `/clickup/tasks/generate-tasks-from-summary`
2. POST `/clickup/tasks/verify-from-summary`
3. POST `/clickup/tasks/save-summary-tasks`

---

## AI Components

- GenerateTaskFromSummaryUseCase
- ClickUpTaskFromSummaryGeneratorAgent
- TaskFromSummaryVerifierAgent

---

## Output

- structured tasks
- action type: `create | update`

---

# 3. ClickUp Tasks — Backlog Flow

## Goal
Convert backlog → ClickUp tasks

---

## Flow

1. generate-tasks-from-backlog
2. verify-from-backlog
3. save-backlog-tasks

---

## Components

- GenerateTaskFromBacklogUseCase
- ClickUpTaskFromBacklogGeneratorAgent
- TaskFromBacklogVerifierAgent

---

# 4. Task Status AI

## Goal
Natural language task search + completion verification

---

## Flow

- `/task-status/search`
- `/task-status/synthesize`

---

## AI Logic

- semantic search on tasks
- GitHub commit correlation
- completion inference

---

# 5. Project Status AI

## Goal
Compute project health overview

---

## Metrics

- task distribution
- stale tasks
- unverified done tasks
- recent activity

---

## Endpoint

- POST `/project-status/status`

---

# 6. Weekly Summary AI

## Goal
Generate weekly project report

---

## Includes

- ClickUp tasks activity
- GitHub commits
- deployments
- project narrative summary

---

## Endpoint

- POST `/weekly-summary/summary`

---

# 7. Commit-to-Task Traceability

## Goal
Map Git commit → ClickUp task

---

## Endpoint

- POST `/commit-traceability/find-task-by-commit`

---

## Output

- FOUND
- NOT_FOUND
- CLICK_UP_EMPTY

---

## Core Logic

- semantic similarity (commit ↔ task)
- space filtering
- ranking of candidates

---

# 8. AI Design Pattern

All AI workflows follow a consistent pattern:

### Step 1 — Input Parsing
- DTO validation
- context extraction

### Step 2 — Orchestration
- workflow controller (use case)

### Step 3 — Tool Execution
- search
- validation
- summarization

### Step 4 — LLM Agents
- reasoning
- classification
- generation

### Step 5 — Structured Output
- DTO response
- deterministic format

---

# 9. Key Design Principles

- deterministic outputs
- modular tools
- reusable agents
- testable pipelines
- streaming when needed (SSE)