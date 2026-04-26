import { BASE_PATH } from '@/api/base';
import type { ReplyBacklogStreamRequest, ReplyStreamRequest, StartBacklogRequest } from '@/api/api';
import { authService } from '@/services/auth-service';
import type { ApiErrorType } from '@/types/api-error-type';
import { SseError } from '@/types/sse-error';


const SSE_HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'text/event-stream',
};

let globalRefreshLock: Promise<void> | null = null;

function buildEndpointUrl(endpoint: string): string {
  return `${BASE_PATH}${endpoint}`;
};

function buildRequestInit(body: unknown): RequestInit {
  return {
    method: 'POST',
    headers: SSE_HEADERS,
    credentials: 'include',
    body: JSON.stringify(body),
  };
};

async function refreshSessionWithLock(): Promise<void> {
  if (globalRefreshLock) {
    return globalRefreshLock;
  }

  globalRefreshLock = authService.refresh().finally(() => {
    globalRefreshLock = null;
  });

  return globalRefreshLock;
};

async function refreshOrRedirect(): Promise<void> {
  try {
    await refreshSessionWithLock();
  } catch {
    await authService.logout();
    window.location.href = '/login';
    throw new Error('Session expired. Redirecting to login.');
  }
};

async function fetchWithAuthRetry(url: string, init: RequestInit): Promise<Response> {
  const response = await fetch(url, init);
  if (response.status !== 401) {
    return response;
  }

  await refreshOrRedirect();
  return fetch(url, init);
};

async function assertSseResponse(response: Response): Promise<ReadableStream<Uint8Array>> {
  if (!response.ok || !response.body) {
    const message = await buildErrorMessage(response);
    const errorType = classifySseError(response.status);
    throw new SseError(message, response.status, errorType);
  }
  return response.body;
}

function normalizeUnknownError(error: unknown, endpoint: string): Error {
  if (error instanceof Error) {
    return error;
  }

  return new Error(`BacklogGenerationService ${endpoint} failed.`);
};

async function postStream(endpoint: string, body: unknown): Promise<ReadableStream<Uint8Array>> {
  try {
    const url = buildEndpointUrl(endpoint);
    const init = buildRequestInit(body);
    const response = await fetchWithAuthRetry(url, init);
    return assertSseResponse(response);
  } catch (error) {
    if (error instanceof SseError) {
      throw error; 
    }
    throw normalizeUnknownError(error, endpoint);
  }
};

async function safeParse(response: Response) {
  try {
    return await response.json();
  } catch {
    return await response.text();
  }
};

async function buildErrorMessage(response: Response): Promise<string> {
  const payload = await safeParse(response);

  if (typeof payload === 'string' && payload.trim().length > 0) {
    return payload;
  }

  if (payload && typeof payload === 'object') {
    if ('error' in payload && typeof (payload as any).error === 'object') {
      const msg = (payload as any).error?.message;
      if (typeof msg === 'string' && msg.trim()) return msg;
    }
    if ('detail' in payload) {
      const detail = (payload as { detail?: string | string[] }).detail;
      if (Array.isArray(detail)) return detail.join(', ');
      if (typeof detail === 'string' && detail.trim()) return detail;
    }
    if ('message' in payload && typeof (payload as any).message === 'string') {
      return (payload as any).message;
    }
  }

  return `Request failed with status ${response.status}.`;
};

export const backlogGenerationService = {
  async start(request: StartBacklogRequest): Promise<ReadableStream<Uint8Array>> {
    return postStream('/backlog/start', request);
  },

  async reply(request: ReplyStreamRequest): Promise<ReadableStream<Uint8Array>> {
    return postStream('/backlog/reply', request);
  },

  async replyBacklog(request: ReplyBacklogStreamRequest): Promise<ReadableStream<Uint8Array>> {
    return postStream('/backlog/reply/backlog', request);
  },
};

function classifySseError(status: number): ApiErrorType {
  if (status === 401 || status === 403) 
    return 'auth_error';
  if (status >= 500 && status !== 502 && status !== 503) 
    return 'server_error';
  return 'backend_error';
};

export const backlogService = backlogGenerationService;