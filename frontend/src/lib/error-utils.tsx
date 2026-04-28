import { showErrorToast } from "@/components/global-toaster";
import { authService } from "@/services/auth-service";
import type { ApiErrorType } from "@/types/api-error-type";
import type { NavigateFunction } from "react-router-dom";

let pendingBackendMessages: string[] = [];
let batchScheduled = false;
const recentErrors = new Set<string>();

const scheduleFlush = () => {
  if (batchScheduled) 
    return;
  batchScheduled = true;
  setTimeout(() => {
    flushBackendErrors();
    batchScheduled = false;
  }, 0);
};

const flushBackendErrors = () => {
  if (pendingBackendMessages.length === 0) return;

  const unique = [...new Set(pendingBackendMessages)];

  if (unique.length === 1) {
    showErrorToast(unique[0], 'Operation failed');
  } else {
    showErrorToast(
      <div>
        <strong style={{ display: 'block', marginBottom: 6 }}>
          {unique.length} errors occurred
        </strong>
        <ul style={{ margin: 0, paddingLeft: 16 }}>
          {unique.map((msg, i) => (
            <li key={i} style={{ marginBottom: 2, fontSize: '0.85em' }}>
              {msg}
            </li>
          ))}
        </ul>
      </div>,
      '',
    );
  }

  pendingBackendMessages = [];
};

const queueBackendError = (message: string) => {
  pendingBackendMessages.push(message);
  scheduleFlush();
};

const deduplicatedError = (key: string, fn: () => void, ttl = 3000) => {
  if (recentErrors.has(key)) return;
  recentErrors.add(key);
  fn();
  setTimeout(() => recentErrors.delete(key), ttl);
};

export const defaultOnError =
  (navigate?: NavigateFunction) =>
  async (errorType: ApiErrorType, message: string) => {

    if (errorType === 'backend_error') {
      queueBackendError(message);
      return;
    }

    deduplicatedError('session_error', async () => {
      await authService.logout();
      if (navigate) navigate('/login');
      showErrorToast('A server error occurred. Please try again later.');
    });
  };