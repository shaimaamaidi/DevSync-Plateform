import { BASE_PATH } from '@/api/base';
import type {
  ReplyBacklogStreamRequest,
  ReplyStreamRequest,
  StartBacklogRequest
} from '@/api/api';
import { authService } from '@/services/auth-service';
import {
  resolveErrorAction,
  extractErrorCode,
} from '@/utils/error-handler';
import { emitAxiosError } from '@/api/axios-interceptor';

const SSE_HEADERS = {
  'Content-Type': 'application/json',
  Accept: 'text/event-stream',
};

let globalRefreshLock: Promise<void> | null = null;

function buildEndpointUrl(endpoint: string): string {
  return `${BASE_PATH}${endpoint}`;
}

function buildRequestInit(body: unknown): RequestInit {
  return {
    method: 'POST',
    headers: SSE_HEADERS,
    credentials: 'include',
    body: JSON.stringify(body),
  };
}

async function refreshSessionWithLock(): Promise<void> {
  if (globalRefreshLock) {
    return globalRefreshLock;
  }

  globalRefreshLock = authService.refresh().finally(() => {
    globalRefreshLock = null;
  });

  return globalRefreshLock;
}

async function refreshOrRedirect(): Promise<void> {
  try {
    await refreshSessionWithLock();
  } catch {
    try {
      await authService.logout();
    } catch {
      // silence
    }
    emitAxiosError({
      action: 'LOGOUT',
      message: 'Session expirée',
      code: 'INVALID_TOKEN',
      status: 401,
    });
    throw new Error('Session expired. Redirecting to login.');
  }
}

async function fetchWithAuthRetry(url: string, init: RequestInit): Promise<Response> {
  const response = await fetch(url, init);
  if (response.status !== 401) {
    return response;
  }

  await refreshOrRedirect();
  return fetch(url, init);
}

async function buildErrorMessage(response: Response): Promise<string> {
  try {
    const payload = await response.json().catch(() => response.text());

    if (typeof payload === 'string' && payload.trim().length > 0) {
      return payload;
    }

    if (payload && typeof payload === 'object') {
      if ('error' in payload && typeof (payload as any).error === 'object') {
        const msg = (payload as any).error?.message;
        if (typeof msg === 'string' && msg.trim()) return msg;
      }
      if ('detail' in payload) {
        const detail = (payload as { detail?: any }).detail;
        if (Array.isArray(detail)) {
          return detail
            .map((item: any) => {
              const field = item.loc?.slice(1).join(' → ') ?? 'field';
              return `${field}: ${item.msg}`;
            })
            .join(', ');
        }
        if (typeof detail === 'string' && detail.trim()) return detail;
      }
      if ('message' in payload && typeof (payload as any).message === 'string') {
        return (payload as any).message;
      }
    }
  } catch {
    // ignore parse errors
  }

  return `Request failed with status ${response.status}.`;
}

function buildErrorLike(status: number, data: unknown) {
  return { response: { status, data } };
}

async function assertSseResponse(response: Response): Promise<ReadableStream<Uint8Array>> {
  if (!response.ok || !response.body) {
    const message = await buildErrorMessage(response);
    const errorLike = buildErrorLike(response.status, { message });
    const action = resolveErrorAction(errorLike);
    const code = extractErrorCode(errorLike);
    const emitAction: 'LOGOUT' | 'RETRY' | 'NOTIFY' | null =
      action === 'SILENT' ? null : action;

    if (emitAction) {
      emitAxiosError({ action: emitAction, message, code, status: response.status });
    }

    throw new Error(message);
  }
  return response.body;
}

async function postStream(endpoint: string, body: unknown): Promise<ReadableStream<Uint8Array>> {
  const url = buildEndpointUrl(endpoint);
  const init = buildRequestInit(body);
  const response = await fetchWithAuthRetry(url, init);
  return assertSseResponse(response);
}

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

export const backlogService = backlogGenerationService;