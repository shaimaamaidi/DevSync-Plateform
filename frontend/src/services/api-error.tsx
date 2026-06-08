import { authService } from "@/services/auth-service";
import { resolveErrorAction, withErrorHandling } from "@/utils/error-handler";
import {
  LOGOUT_MESSAGES,
  type ApiErrorMeta,
  type ErrorAction,
} from "@/types/api-error-type";
import type { NavigateFunction } from "react-router-dom";
import { dismissToast, showErrorToast, TOAST_IDS } from "@/components/global-toaster";
import type { ReactNode } from "react";

export { withErrorHandling };
export const handleApiError = resolveErrorAction;


function getLogoutMessage(code?: string | null): string {
  if (code && code in LOGOUT_MESSAGES) return LOGOUT_MESSAGES[code];
  return LOGOUT_MESSAGES["session_expired"];
}

async function redirectToLogin(
  navigate: NavigateFunction | undefined,
  reason: string,
  logoutFn?: () => Promise<void> 
) {
  await new Promise((res) => setTimeout(res, 3000)); 
  try { await logoutFn?.(); } catch { /* ignored */ } 
  navigate
    ? navigate(`/login?reason=${reason}`)
    : (window.location.href = `/login?reason=${reason}`);
}


const recentErrors = new Set<string>();

const deduplicatedError = (key: string, fn: () => Promise<void> | void, ttl = 3000) => {
  if (recentErrors.has(key)) return;
  recentErrors.add(key);
  Promise.resolve(fn()).catch(console.error);
  setTimeout(() => recentErrors.delete(key), ttl);
};


let pendingMessages: string[] = [];
let batchScheduled = false;
const recentToastMessages = new Set<string>();

const scheduleFlush = () => {
  if (batchScheduled) return;
  batchScheduled = true;
  setTimeout(() => {
    flushErrors();
    batchScheduled = false;
  }, 0);
};

const flushErrors = () => {
  if (pendingMessages.length === 0) return;
  const unique = [...new Set(pendingMessages)];
  pendingMessages = [];

  const content: ReactNode =
    unique.length === 1
      ? `Operation failed: ${unique[0]}`
      : (
        <div>
          <strong style={{ display: "block", marginBottom: 6 }}>
            {unique.length} errors occurred
          </strong>
          <ul style={{ margin: 0, paddingLeft: 16 }}>
            {unique.map((msg, i) => (
              <li key={i} style={{ marginBottom: 2, fontSize: "0.85em" }}>
                {msg}
              </li>
            ))}
          </ul>
        </div>
      );

  dismissToast(TOAST_IDS.BATCH_ERRORS);
  setTimeout(() => {
    showErrorToast(content, { toastId: TOAST_IDS.BATCH_ERRORS, autoClose: 4000 });
  }, 100);
};

const queueError = (message: string) => {
  if (recentToastMessages.has(message)) return;
  recentToastMessages.add(message);
  setTimeout(() => recentToastMessages.delete(message), 3000);
  pendingMessages.push(message);
  scheduleFlush();
};


export const defaultOnError =
  (navigate?: NavigateFunction) =>
  async (action: ErrorAction, message: string, meta?: ApiErrorMeta) => {

    if (action === "NETWORK_DOWN") {
      deduplicatedError("network_down", () => {
        showErrorToast(LOGOUT_MESSAGES["network_down"], {
          toastId: TOAST_IDS.NETWORK_DOWN,
          autoClose: 4000,
          closeOnClick: true,
        });
      });
      return;
    }

    if (action === "SILENT") return;

    if (action === "LOGOUT") {
      deduplicatedError("session_error", async () => {
        const reason = meta?.code ?? "session_expired";
        showErrorToast(getLogoutMessage(meta?.code), {
          toastId: TOAST_IDS.SESSION_ERROR,
          autoClose: 4000,
          closeOnClick: false,
          draggable: false,
        });
        await redirectToLogin(navigate, reason, () => authService.logout());
      });
      return;
    }

    if (action === "RETRY_THEN_LOGOUT") {
      deduplicatedError("retry_then_logout", async () => {
        showErrorToast(LOGOUT_MESSAGES["retry_then_logout"], {
          toastId: TOAST_IDS.RETRY_THEN_LOGOUT,
          autoClose: 4000,
          closeOnClick: false,
          draggable: false,
        });
      await redirectToLogin(navigate, "retry_then_logout", () => authService.logout());
      });
      return;
    }

    if (action === "RETRY_THEN_SERVICE_ERROR") {
      deduplicatedError("service_error", () => {
        showErrorToast(LOGOUT_MESSAGES["service_error"], {
          toastId: TOAST_IDS.SERVICE_ERROR,
          autoClose: 5000,
          closeOnClick: true,
        });
      });
      return;
    }

    if (action === "RETRY_THEN_DATA_ERROR") {
      deduplicatedError("data_error", () => {
        showErrorToast(LOGOUT_MESSAGES["data_error"], {
          toastId: TOAST_IDS.DATA_ERROR,
          autoClose: 5000,
          closeOnClick: true,
        });
      });
      return;
    }

    const isNetworkMessage =
      message === "Network Error" || message === "Network is down";
    if (isNetworkMessage) return;

    queueError(message);
  };
