# Frontend API Reference

This document lists the backend endpoints consumed by the frontend services. The generated client in `src/api` is the source of request and response types.

## Authentication

- `POST /auth/login` — sign in and receive session tokens
- `POST /auth/refresh` — refresh the session
- `POST /auth/logout` — revoke the refresh token
- `GET /auth/me` — load the current member

Authenticated requests use the session cookie and Axios credentials configuration.

## Repositories and Members

- `GET /repo/all`
- `GET /repo/details`
- `GET /repo/{id}`
- `POST /repo/`
- `PUT /repo/{id}`
- `DELETE /repo/{id}`
- `GET /member/all/with-repos`
- `POST /member/`
- `PUT /member/{id}`
- `DELETE /member/{id}`

## ClickUp Workspace

- `GET /clickup/light`
- `GET /clickup/`
- `POST /clickup/`
- `PUT /clickup/{space_id}`
- `DELETE /clickup/{space_id}`
- `GET /clickup/structure/spaces/{space_id}/metadata`
- `POST /clickup/structure/spaces/register`
- `POST /clickup/structure/spaces`
- `DELETE /clickup/structure/spaces/{space_id}`
- `POST /clickup/structure/folders`
- `POST /clickup/structure/lists`
- `POST /clickup/structure/lists/{list_id}/statuses`
- `POST /clickup/structure/members/invite`
- `DELETE /clickup/structure/members/{member_id}`

## ClickUp Tasks

- `GET /clickup/tasks/spaces/{space_id}`
- `POST /clickup/tasks/manage`
- `PUT /clickup/tasks/manage/{space_id}`
- `DELETE /clickup/tasks/manage/{task_id}`
- `POST /clickup/tasks/generate-tasks-from-summary`
- `POST /clickup/tasks/verify-from-summary`
- `POST /clickup/tasks/save-summary-tasks`
- `POST /clickup/tasks/generate-tasks-from-backlog`
- `POST /clickup/tasks/verify-from-backlog`
- `POST /clickup/tasks/save-backlog-tasks`

## GitHub and Deployments

- `POST /associate/space` — associate a repository with a ClickUp space
- `GET /deployment/list` — load deployments for a repository

## Project Insights

- `POST /task-status/search` — search tasks from a natural-language request
- `POST /task-status/synthesize` — synthesize task status
- `POST /project-status/status` — calculate project status
- `POST /weekly-summary/summary` — generate a weekly summary
- `POST /commit-traceability/find-task-by-commit` — map a commit to a task

## Streaming Backlog API

The backlog service uses authenticated `POST` requests with `Accept: text/event-stream`:

- `POST /backlog/start`
- `POST /backlog/reply`
- `POST /backlog/reply/backlog`
- `POST /backlog/delivery-plan`

The response body is consumed as a `ReadableStream<Uint8Array>` and parsed by `src/utils/stream-parser.ts`.

## Error Handling

The frontend has two error paths: Axios for normal API calls and `fetch` streams for backlog workflows. Both paths normalize backend errors into user-facing messages.

The expected structured error shape is:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Authentication failures, rate limits, service errors, data errors, and network loss are routed through the shared error event system.

### Normal API Calls (Axios)

Normal API services use the generated Axios client and the shared interceptor in `src/api/axios-interceptor.ts`.

#### Session refresh

- A `401` response triggers one session refresh attempt for the original request.
- The original request is replayed once after a successful refresh.
- Concurrent `401` responses wait for the same refresh operation instead of starting separate refresh calls.
- Once refresh succeeds, every request waiting in the queue is replayed with its original configuration.
- Login, refresh, and logout requests never trigger another refresh.
- If refresh fails, queued requests are rejected, the session is cleared, and a `LOGOUT` event is emitted.

#### Automatic retry limits

Automatic retries are allowed only for `GET`, `HEAD`, and `OPTIONS`. Normal `POST`, `PUT`, and `DELETE` calls are not replayed by the generic Axios retry policy because they may have side effects. They are handled by the calling service and `withErrorHandling`.

| Error action | Automatic retries after the first request | Delay sequence | Final behavior |
|---|---:|---|---|
| `RETRY_THEN_LOGOUT` | 2 | 1s, 2s | Logout notification |
| `RETRY_THEN_SERVICE_ERROR` | 2 | 1s, 2s | Service error notification |
| `RETRY_THEN_DATA_ERROR` | 3 | 500ms, 1s, 2s | Data error notification |

For `429` responses with `CLICKUP_RATE_LIMIT` or `GITHUB_RATE_LIMIT`, each retry waits 5 seconds instead of the normal exponential delay. The same retry count still applies.

The retry counter is stored per request and is removed after a successful response or after the policy is exhausted.

#### Error classification

- `401` or invalid session/configuration codes: logout or session recovery
- `403` and `422`: notification without automatic retry
- `429`, `502`, and `503`: service retry policy
- `500`: data retry policy
- persistence and database codes: data retry policy
- `STREAM_CANCELLED`: silent, with no retry or notification
- network loss: broadcasts `NETWORK_DOWN` and rejects the request

`withErrorHandling` catches the final error, resolves its action, extracts the status and error code, and forwards it to the page-level error handler. It does not add another retry loop.

### Streaming API Calls (fetch/SSE)

Backlog streaming calls use `backlog-generation-service.ts` and `fetch`, not the Axios interceptor.

#### Request and authentication behavior

- Requests are authenticated `POST` calls with `Accept: text/event-stream`.
- A `401` response triggers one shared refresh operation and one replay of the stream request.
- Concurrent stream requests share the same refresh lock.
- If refresh fails, the session is cleared and a `LOGOUT` event is emitted.
- There is no generic automatic retry after a stream has started and then disconnects. Replaying a partially consumed stream could duplicate generated content, so the error is surfaced to the workflow UI.

#### Stream parsing and failures

`src/utils/stream-parser.ts` reads the response as a `ReadableStream<Uint8Array>` and processes `data:` frames.

- Valid text chunks are appended incrementally and sent to the chat UI.
- Thread identifiers, tool calls, backlog previews, delivery-plan previews, and invalid-description messages are extracted from events.
- Structured business errors inside a stream are converted to an error event and stop consumption.
- Malformed SSE lines are ignored; a valid later frame can still be processed.
- Connection failures emit `NETWORK_DOWN` for network errors or `STREAM_EXECUTION_ERROR` for other stream failures.
- Voluntary cancellation uses `STREAM_CANCELLED` and remains silent.

The stream parser does not retry and does not refresh the session itself; refresh is handled before the stream is returned by the backlog service.

### Error Event Consumers

`onAxiosError` and `onNetworkChange` allow global UI components to react to errors and connectivity changes. Page-level workflows use `withErrorHandling` for normal requests and the stream parser callbacks for incremental stream feedback.

### Concurrent Failures and Toasts

When several API calls fail for the same reason at approximately the same time:

- the refresh lock prevents multiple refresh calls;
- requests that received `401` wait for that refresh and are all replayed after it succeeds;
- after retry exhaustion, the global error handler deduplicates `NETWORK_DOWN`, session, service, and data errors by category for 3 seconds;
- therefore, one shared toast is displayed for the same categorized failure during that window, even if several requests emitted the error;
- unclassified messages are deduplicated by message for 3 seconds and collected into one batch toast for the current error burst;
- different failure categories can still produce separate toasts.

This deduplication applies to notifications, not to the requests themselves: each queued request is still resolved or rejected independently.