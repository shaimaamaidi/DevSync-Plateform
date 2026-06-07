import { authService } from "@/services/auth-service";
import {
  resolveErrorAction,
  withErrorHandling,
} from "@/utils/error-handler";
import { LOGOUT_MESSAGES, type ApiErrorMeta, type ErrorAction } from "@/types/api-error-type";
import type { NavigateFunction } from "react-router-dom";
import { toast } from "react-toastify";

export {
  withErrorHandling,
};

export const handleApiError = resolveErrorAction;


function getLogoutMessage(code?: string | null): string {
  if (code && code in LOGOUT_MESSAGES) return LOGOUT_MESSAGES[code];
  return LOGOUT_MESSAGES["session_expired"];
}


let pendingMessages: string[] = [];
let batchScheduled = false;
const recentErrors = new Set<string>();
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

  const content =
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

  toast.dismiss("batch_errors");
  setTimeout(() => {
    toast.error(content, {
      toastId: "batch_errors",
      autoClose: 4000,
    });
  }, 100);
};

const queueError = (message: string) => {
  if (recentToastMessages.has(message)) return;
  recentToastMessages.add(message);
  setTimeout(() => recentToastMessages.delete(message), 3000);

  pendingMessages.push(message);
  scheduleFlush();
};

const deduplicatedError = (key: string, fn: () => void, ttl = 3000) => {
  if (recentErrors.has(key)) return;
  recentErrors.add(key);
  fn();
  setTimeout(() => recentErrors.delete(key), ttl);
};


const MAX_RETRIES = 3;
const BASE_DELAY_MS = 1000;

async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  attempt = 1,
): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    if (attempt >= MAX_RETRIES) throw err;
    await new Promise((res) => setTimeout(res, BASE_DELAY_MS * attempt));
    return retryWithBackoff(fn, attempt + 1);
  }
}


export const defaultOnError =
  (navigate?: NavigateFunction) =>
  async (action: ErrorAction, message: string, meta?: ApiErrorMeta) => {

    if (action === "NETWORK_DOWN") {
      deduplicatedError("network_down", () => {
        toast.error(LOGOUT_MESSAGES["network_down"], {
          autoClose: 4000,
          closeOnClick: true,
          toastId: "network_down",
        });
      });
      return;
    }

    if (action === "SILENT") return;

    if (action === "LOGOUT") {
      deduplicatedError("session_error", async () => {
        const reason = meta?.code ?? "session_expired";
        const toastMsg = getLogoutMessage(meta?.code);

        toast.error(toastMsg, {
          autoClose: 4000,
          closeOnClick: false,
          draggable: false,
          toastId: "session_error",
        });

        await new Promise((res) => setTimeout(res, 3000));

        await authService.logout();
        navigate
          ? navigate(`/login?reason=${reason}`)
          : (window.location.href = `/login?reason=${reason}`);
      });
      return;
    }

    if (action === "RETRY") {
      deduplicatedError("server_down", async () => {
        const toastMsg = LOGOUT_MESSAGES["server_down"];

        toast.error(
          toastMsg,
          {
            autoClose: 4000,      
            closeOnClick: false,  
            draggable: false,
            toastId: "server_down", 
          }
        );
        await new Promise((res) => setTimeout(res, 3000));

        await authService.logout();
        navigate
          ? navigate("/login?reason=server_down")
          : (window.location.href = "/login?reason=server_down");
      });
      return;
    }

    const isNetworkMessage = message === "Network Error" ||  message === "Network is down";

    if (isNetworkMessage) 
      return;

    queueError(message);
  };

export { retryWithBackoff };