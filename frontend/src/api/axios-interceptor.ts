import axios from 'axios';
import { authService } from '@/services/auth-service';

function redirectToLogin() {
  window.location.href = '/login';
}

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response && error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          await authService.refresh();
          return axios(originalRequest);
        } catch (refreshError) {
          authService.logout();
          redirectToLogin();
          return Promise.reject(refreshError);
        }
      }
      if (error.response && error.response.status === 401) {
        authService.logout();
        redirectToLogin();
      }
      return Promise.reject(error);
    }
  );
}
