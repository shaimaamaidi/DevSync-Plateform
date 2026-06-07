import type { ReactNode } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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

export function showErrorToast(message: ReactNode, title = 'Operation failed') {
  const content =
    typeof message === 'string' ? (
      `${title ? title + ': ' : ''}${message}`
    ) : (
      message
    );

  toast.error(content, {
    toastId: typeof message === "string" ? `error_${message}` : "error_complex",
  });
}

export function showSuccessToast(message: string, title = 'Success') {
  toast.success(`${title ? title + ': ' : ''}${message}`);
}