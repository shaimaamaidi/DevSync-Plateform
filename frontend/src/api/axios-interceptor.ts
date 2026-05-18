import axios from "axios";
import { authService } from "@/services/auth-service";
import {
  resolveErrorAction,
  normalizeErrorMessage,
  extractErrorCode,
} from "@/utils/error-handler";

export interface AxiosErrorEvent {
  action: "LOGOUT" | "RETRY" | "NOTIFY";
  message: string;
  code?: string | null;
  status?: number;
}

type AxiosErrorListener = (event: AxiosErrorEvent) => void;
const errorListeners: AxiosErrorListener[] = [];

export function onAxiosError(listener: AxiosErrorListener): () => void {
  errorListeners.push(listener);
  return () => {
    const idx = errorListeners.indexOf(listener);
    if (idx !== -1) errorListeners.splice(idx, 1);
  };
}

export function emitAxiosError(event: AxiosErrorEvent) {
  errorListeners.forEach((cb) => cb(event));
}

function emitError(event: AxiosErrorEvent) {
  emitAxiosError(event);
}

let isRefreshing = false;
let pendingRequests: Array<() => void> = [];
const retryCountMap = new Map<string, number>();
let requestIdCounter = 0;

function getRetryKey(config: any): string {
  if (!config._retryId) {
    config._retryId = ++requestIdCounter;
  }
  return String(config._retryId);
}

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => {
      const key = String((response.config as any)._retryId);
      if (key) retryCountMap.delete(key);
      return response;
    },

    async (error) => {
      const originalRequest = error.config;
      const status = error.response?.status;
      const isAuthRequest = originalRequest?.url?.includes("/auth/");

      if (status === 401 && !originalRequest._retry && !isAuthRequest) {
        originalRequest._retry = true;

        if (isRefreshing) {
          return new Promise((resolve) => {
            pendingRequests.push(() => resolve(axios(originalRequest)));
          });
        }

        isRefreshing = true;
        try {
          await authService.refresh();
          pendingRequests.forEach((cb) => cb());
          pendingRequests = [];
          return axios(originalRequest);
        } catch (refreshError) {
          pendingRequests = [];
          try { await authService.logout(); } catch { /* ignored */ }
          emitError({
            action: "LOGOUT",
            message: "Session expired",
            code: "INVALID_TOKEN",
            status: 401,
          });
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      const action = resolveErrorAction(error);
      const message = normalizeErrorMessage(error);
      const code = extractErrorCode(error);

      if (action === "SILENT") return Promise.reject(error);

      if (action === "RETRY") {
        const retryKey = getRetryKey(originalRequest);
        const attempt = retryCountMap.get(retryKey) ?? 0;

        if (attempt < 3) {
          retryCountMap.set(retryKey, attempt + 1);
          await new Promise((res) => setTimeout(res, 1000 * (attempt + 1)));
          return axios(originalRequest);
        }

        retryCountMap.delete(retryKey);
        emitError({ action: "RETRY", message, code, status });
        return Promise.reject(error);
      }

      emitError({ action, message, code, status });
      return Promise.reject(error);
    }
  );
}