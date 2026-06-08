export type ErrorAction =
  | "LOGOUT"
  | "RETRY_THEN_LOGOUT"
  | "RETRY_THEN_SERVICE_ERROR"
  | "RETRY_THEN_DATA_ERROR"
  | "NOTIFY"
  | "SILENT"
  | "NETWORK_DOWN";

export const REASON_MESSAGES: Record<string, string> = {
  server_down: "The server is unavailable. Please try again later.",
  service_error: "A service error occurred. Please try again later.",
  data_error: "A data error occurred. Please try again later.",
  session_expired: "Your session has expired. Please sign in again.",
  INVALID_TOKEN: "Your session has expired. Please sign in again.",
};

export const LOGOUT_MESSAGES: Record<string, string> = {
  INVALID_TOKEN: "Your session has expired. Please sign in again.",
  UNAUTHORIZED: "Your session has expired. Please sign in again.",
  TOKEN_EXPIRED: "Your session has expired.",
  MISSING_ENV_VARIABLE: "Server configuration error. Contact the administrator.",
  MISSING_AZURE_CONFIG: "Azure configuration error. Contact the administrator.",
  MISSING_CLICKUP_CONFIG: "ClickUp configuration error. Contact the administrator.",
  AGENT_INITIALIZATION_ERROR: "Unable to initialize the agent. Contact the administrator.",
  retry_then_logout: "Session could not be restored. Please sign in again.",
  service_error: "The service is unavailable after multiple attempts. Try again later.",
  data_error: "A data error persisted after multiple attempts. Try again later.",
  session_expired: "Your session has expired. Please sign in again.",
  network_down: "Connection lost. Please check your internet connection.",
};

export interface ApiError {
  status: number;
  code: string;
  message: string;
}

export interface ApiErrorMeta {
  status?: number;
  code?: string | null;
}