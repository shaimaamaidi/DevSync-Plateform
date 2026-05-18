export type ErrorAction = "LOGOUT" | "RETRY" | "NOTIFY" | "SILENT";

export const REASON_MESSAGES: Record<string, string> = {
  server_down: "The server is unavailable. Please try again later.",
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
  server_down: "The server is unavailable after multiple attempts. Try again later.",
  session_expired: "Your session has expired. Please sign in again.",
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
