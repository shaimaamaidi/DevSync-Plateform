import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export function GlobalSuccessToaster() {
  return <ToastContainer position="top-right" autoClose={4000} hideProgressBar={false} newestOnTop closeOnClick pauseOnFocusLoss draggable pauseOnHover />;
}

export function showSuccessToast(message: string, title = 'Succès') {
  toast.success(`${title ? title + ': ' : ''}${message}`);
}
