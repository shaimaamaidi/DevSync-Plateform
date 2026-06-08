import axios from "axios";
import { authService } from "@/services/auth-service";
import {
  resolveErrorAction,
  normalizeErrorMessage,
  extractErrorCode,
} from "@/utils/error-handler";
import { RETRY_POLICIES } from "@/api/error-codes";

export interface AxiosErrorEvent {
  action: "LOGOUT" | "RETRY_THEN_LOGOUT" | "RETRY_THEN_SERVICE_ERROR" | "RETRY_THEN_DATA_ERROR" | "NOTIFY" | "SILENT" | "NETWORK_DOWN";
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

function emitAxiosError(event: AxiosErrorEvent) {
  errorListeners.forEach((cb) => cb(event));
}

export function emitAxiosErrorNetworkOnly(event: AxiosErrorEvent) {
  if (event.action === "NETWORK_DOWN") {
    errorListeners.forEach((cb) => cb(event));
  }
}

let isRefreshing = false;
let pendingRequests: Array<{
  resolve: (value: any) => void;
  reject: (reason: any) => void;
  config: any;
}> = [];

const retryCountMap = new Map<string, number>();
let requestIdCounter = 0;

let isNetworkDown = false;
type NetworkListener = (isDown: boolean) => void;
const networkListeners: NetworkListener[] = [];

export function onNetworkChange(listener: NetworkListener): () => void {
  networkListeners.push(listener);
  return () => {
    const idx = networkListeners.indexOf(listener);
    if (idx !== -1) networkListeners.splice(idx, 1);
  };
}

function setNetworkDown(value: boolean) {
  if (isNetworkDown === value) return;
  isNetworkDown = value;
  networkListeners.forEach((cb) => cb(value));
}


const REFRESH_SKIP_URLS = ["/auth/refresh", "/auth/login", "/auth/logout"];

function shouldSkipRefresh(url?: string): boolean {
  if (!url) return false;
  return REFRESH_SKIP_URLS.some((skip) => url.includes(skip));
}

function getRetryKey(config: any): string {
  if (!config._retryId) config._retryId = ++requestIdCounter;
  return String(config._retryId);
}

function getRetryPolicy(action: AxiosErrorEvent["action"]) {
  switch (action) {
    case "RETRY_THEN_LOGOUT":
      return RETRY_POLICIES.RETRY_THEN_LOGOUT;
    case "RETRY_THEN_SERVICE_ERROR":
      return RETRY_POLICIES.RETRY_THEN_SERVICE_ERROR;
    case "RETRY_THEN_DATA_ERROR":
      return RETRY_POLICIES.RETRY_THEN_DATA_ERROR;
    default:
      return null;
  }
}

function isRateLimitCode(code: string | null): boolean {
  return (
    code === "CLICKUP_RATE_LIMIT" ||
    code === "GITHUB_RATE_LIMIT"
  );
}

function computeDelay(
  baseDelayMs: number,
  attempt: number,
  isRateLimit: boolean
): number {
  if (isRateLimit) return 5000; 
  return baseDelayMs * Math.pow(2, attempt); 
}


export function setupAxiosInterceptors() {

  axios.interceptors.request.use((config) => {
    if (isNetworkDown) {
      return Promise.reject(new Error("Network is down"));
    }
    return config;
  });

  axios.interceptors.response.use(
    (response) => {
      setNetworkDown(false);
      const key = String((response.config as any)._retryId);
      if (key) retryCountMap.delete(key);
      return response;
    },

    async (error) => {
      if (error._silent) return Promise.reject(error);

      const isNetworkError =
        error.message === "Network Error" && !error.response;

      if (isNetworkError) {
        setNetworkDown(true);
        emitAxiosError({
          action: "NETWORK_DOWN",
          message: "Network error",
          code: null,
          status: undefined,
        });
        return Promise.reject(error);
      }

      setNetworkDown(false);

      const originalRequest = error.config;
      const status = error.response?.status;

      if (shouldSkipRefresh(originalRequest?.url)) {
        return Promise.reject(error);
      }

      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            pendingRequests.push({ resolve, reject, config: originalRequest });
          });
        }

        isRefreshing = true;

        try {
          await authService.refresh();

          const pending = [...pendingRequests];
          pendingRequests = [];
          pending.forEach(({ resolve, reject, config }) => {
            axios(config).then(resolve).catch(reject);
          });

          return axios(originalRequest);
        } catch (refreshError) {
          const pending = [...pendingRequests];
          pendingRequests = [];
          pending.forEach(({ reject }) => reject(refreshError));

          try { await authService.logout(); } catch { /* ignored */ }

          emitAxiosError({
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

      const policy = getRetryPolicy(action);

      if (policy) {
        const retryKey = getRetryKey(originalRequest);
        const attempt = retryCountMap.get(retryKey) ?? 0;

        if (attempt < policy.maxAttempts && !isNetworkDown) {
          retryCountMap.set(retryKey, attempt + 1);

          const delay = computeDelay(
            policy.baseDelayMs,
            attempt,
            isRateLimitCode(code)
          );

          await new Promise((res) => setTimeout(res, delay));
          return axios(originalRequest);
        }

        retryCountMap.delete(retryKey);

        if (isNetworkDown) return Promise.reject(error);

        emitAxiosError({ action, message, code, status });
        return Promise.reject(error);
      }

      emitAxiosError({ action, message, code, status });
      return Promise.reject(error);
    }
  );
}