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
      pauseOnFocusLoss
      draggable
      pauseOnHover
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

  toast.error(content);
}

export function showSuccessToast(message: string, title = 'Success') {
  toast.success(`${title ? title + ': ' : ''}${message}`);
}