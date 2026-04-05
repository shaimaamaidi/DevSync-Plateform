import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export function GlobalErrorToaster() {
  return <ToastContainer position="top-right" autoClose={4000} hideProgressBar={false} newestOnTop closeOnClick pauseOnFocusLoss draggable pauseOnHover />;
}

export function showErrorToast(message: string, title = 'Operation failed') {
  toast.error(`${title ? title + ': ' : ''}${message}`);
}
