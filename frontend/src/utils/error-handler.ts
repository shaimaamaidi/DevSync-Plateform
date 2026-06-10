import {
  LOGOUT_IMMEDIATELY,
  RETRY_THEN_LOGOUT,
  RETRY_THEN_SERVICE_ERROR,
  RETRY_THEN_DATA_ERROR,
  SILENT_CODES,
  type ErrorCode,
} from "@/api/error-codes";
import type { ApiErrorMeta, ErrorAction } from "@/types/api-error-type";

type ErrorLike = {
  message?: string;
  response?: {
    data?: unknown;
    status?: number;
  };
};

type ErrorListener = (msg: string) => void;

const listeners: ErrorListener[] = [];

export function subscribeToApiError(listener: ErrorListener) {
  listeners.push(listener);
  return () => {
    const idx = listeners.indexOf(listener);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

export function extractErrorCode(err: unknown): string | null {
  try {
    const data = (err as ErrorLike)?.response?.data;
    if (!data || typeof data !== "object") return null;
    return (data as any)?.error?.code ?? (data as any)?.code ?? null;
  } catch {
    return null;
  }
}

export function extractStatusCode(err: unknown): number | null {
  try {
    return (err as ErrorLike)?.response?.status ?? null;
  } catch {
    return null;
  }
}

export function extractAssigneeListFromError(message: string): string[] {
  const match = message.match(/\[([^\]]+)\]/);
  if (!match) return [message];
  return match[1]
    .split(",")
    .map((s) => s.trim().replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

export function normalizeErrorMessage(error: unknown): string {
  if (!error || typeof error !== "object") return "Unknown error";

  const err = error as ErrorLike;
  const data = err.response?.data;

  if (typeof data === "string" && data.trim()) return data;

  if (data && typeof data === "object") {
    const d = data as Record<string, unknown>;

    if ("detail" in d) {
      const detail = d.detail;
      if (Array.isArray(detail)) {
        return detail
          .map((item: any) => {
            const field = item.loc?.slice(1).join(" → ") ?? "field";
            return `${field}: ${item.msg}`;
          })
          .join(", ");
      }
      if (typeof detail === "string") return detail;
    }

    const errorObj = d.error;
    if (errorObj && typeof errorObj === "object") {
      const msg = (errorObj as Record<string, unknown>).message;
      if (typeof msg === "string" && msg.trim()) return msg;
    }

    if (typeof d.message === "string" && d.message.trim()) return d.message;
  }

  if (typeof err.message === "string" && err.message.trim()) return err.message;

  return "Unknown error";
}

export function resolveErrorAction(err: unknown): ErrorAction {
  const status = extractStatusCode(err);
  const code = extractErrorCode(err) as ErrorCode | null;

  const isNetworkError =
    (err as ErrorLike)?.message === "Network Error" &&
    !(err as ErrorLike)?.response;

  if (isNetworkError) return "NETWORK_DOWN";

  if (code && SILENT_CODES.has(code)) return "SILENT";

  if (code && LOGOUT_IMMEDIATELY.has(code)) return "LOGOUT";

  if (status === 401) return "LOGOUT";
  if (status === 403) return "NOTIFY";

  if (status === 422) return "NOTIFY";

  if (code && RETRY_THEN_LOGOUT.has(code)) 
    return "RETRY_THEN_LOGOUT";
  if (code && RETRY_THEN_SERVICE_ERROR.has(code))  
    return "RETRY_THEN_SERVICE_ERROR";
  if (code && RETRY_THEN_DATA_ERROR.has(code))     
    return "RETRY_THEN_DATA_ERROR";

  if (status === 429 || status === 502 || status === 503)
    return "RETRY_THEN_SERVICE_ERROR";

  if (status === 500)
    return "RETRY_THEN_DATA_ERROR";

  return "NOTIFY";
}

export async function withErrorHandling<T>(
  fn: () => Promise<T>,
  context: string,
  onError?: (action: ErrorAction, message: string, meta?: ApiErrorMeta) => void,
): Promise<T | null> {
  try {
    return await fn();
  } catch (err) {
    const action = resolveErrorAction(err);
    const message = normalizeErrorMessage(err);
    const status = extractStatusCode(err);
    const code = extractErrorCode(err);

    if (action === "SILENT" || action === "NETWORK_DOWN") return null;

    if (onError) {
      onError(action, message, { status: status ?? undefined, code });
    } else {
      listeners.forEach((cb) => cb(`[${context}] ${message}`));
    }

    return null;
  }
}