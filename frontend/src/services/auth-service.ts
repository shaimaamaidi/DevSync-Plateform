import type { MemberAuthDTO } from '@/api/api';
import { AuthApi } from '@/api/api';

function setRefreshTokenCookie(value: string) {
  document.cookie = `refresh_token=${encodeURIComponent(value)}; max-age=${REFRESH_TOKEN_MAX_AGE}; path=/; SameSite=Lax; Secure`;
}

function deleteRefreshTokenCookie() {
  document.cookie = `refresh_token=; max-age=0; path=/`;
}

function getRefreshTokenCookie(): string | null {
  const match = document.cookie.match(/(?:^|; )refresh_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

const REFRESH_TOKEN_EXPIRE_DAYS = Number(import.meta.env.VITE_REFRESH_TOKEN_EXPIRE_DAYS || 7);
const REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * REFRESH_TOKEN_EXPIRE_DAYS;

class AuthService {
  async login(credentials: MemberAuthDTO): Promise<void> {
    const api = new AuthApi();
    const { data } = await api.loginAuthLoginPost(credentials);
    setRefreshTokenCookie(data.refresh_token);
  }

  async logout(): Promise<void> {
    const refreshToken = getRefreshTokenCookie();
    if (refreshToken) {
      try {
        const api = new AuthApi();
        await api.logoutAuthLogoutPost(refreshToken);
      } catch {
        // Intentional silent failure
      }
    }
    deleteRefreshTokenCookie();
  }

  async refresh(): Promise<void> {
    const refreshToken = getRefreshTokenCookie();
    if (!refreshToken)
      throw new Error('[AuthService] No refresh token available');
    const api = new AuthApi();
    const { data } = await api.refreshAuthRefreshPost(refreshToken);
    setRefreshTokenCookie(data.refresh_token);
  }

  isAuthenticated(): boolean {
    return !!getRefreshTokenCookie();
  }
}

export const authService = new AuthService();