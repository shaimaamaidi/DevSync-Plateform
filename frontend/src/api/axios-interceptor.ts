import axios from 'axios';

import { authService } from '@/services/auth-service';

let isRefreshing = false;
let pendingRequests: Array<() => void> = [];

function redirectToLogin() {
  window.location.href = '/login';
}

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      const is401 = error.response?.status === 401;
      if (is401 && !originalRequest._retry) {
        originalRequest._retry = true;
         if (isRefreshing) {
          return new Promise((resolve) => {
            pendingRequests.push(() => resolve(axios(originalRequest)));
          });
        }

        isRefreshing = true;

        try {
          await authService.refresh();
          pendingRequests.forEach(cb => cb());
          pendingRequests = [];
          return axios(originalRequest);
        } catch (refreshError) {
          pendingRequests = [];
          await authService.logout();
          redirectToLogin();
          return Promise.reject(refreshError);
        }finally {
          isRefreshing = false;
        }
      }
      return Promise.reject(error);
    }
  );
}
