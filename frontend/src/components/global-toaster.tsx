import type { ReactNode } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


export const TOAST_IDS = {
  NETWORK_DOWN: "network_down",
  SESSION_ERROR: "session_error",
  RETRY_THEN_LOGOUT: "retry_then_logout",
  SERVICE_ERROR: "service_error",
  DATA_ERROR: "data_error",
  BATCH_ERRORS: "batch_errors",
} as const;

export type ToastId = (typeof TOAST_IDS)[keyof typeof TOAST_IDS];


export function GlobalToaster() {
  return (
    <ToastContainer
      position="top-right"
      autoClose={4000}
      hideProgressBar={false}
      newestOnTop
      closeOnClick
      pauseOnFocusLoss={false}
      draggable
      pauseOnHover
      className="!top-4 !right-4 !left-4 sm:!left-auto sm:!w-auto"
    />
  );
}


export function showErrorToast(
  message: ReactNode,
  options?: {
    title?: string;
    toastId?: ToastId | string;
    autoClose?: number;
    closeOnClick?: boolean;
    draggable?: boolean;
  }
) {
  const { title, toastId, autoClose = 4000, closeOnClick = true, draggable = true } = options ?? {};

  const content =
    typeof message === 'string'
      ? `${title ? title + ': ' : ''}${message}`
      : message;

  toast.error(content, {
    toastId: toastId ?? (typeof message === 'string' ? `error_${message}` : 'error_complex'),
    autoClose,
    closeOnClick,
    draggable,
  });
}

export function showSuccessToast(message: string, title = 'Success') {
  toast.success(`${title ? title + ': ' : ''}${message}`);
}

export function dismissToast(toastId: ToastId | string) {
  toast.dismiss(toastId);
}