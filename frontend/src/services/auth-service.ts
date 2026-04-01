import type { MemberAuthDTO } from '@/api/api';
import { AuthApi } from '@/api/api';

function setCookie(name: string, value: string, options: { maxAge?: number; path?: string; sameSite?: 'Lax' | 'Strict'; secure?: boolean } = {}) {
  let cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
  if (options.maxAge) cookie += `; max-age=${options.maxAge}`;
  if (options.path) cookie += `; path=${options.path}`;
  if (options.sameSite) cookie += `; SameSite=${options.sameSite}`;
  if (options.secure) cookie += `; Secure`;
  document.cookie = cookie;
}

function deleteCookie(name: string) {
  document.cookie = `${encodeURIComponent(name)}=; max-age=0; path=/`;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

const REFRESH_TOKEN_COOKIE = 'refresh_token';
const REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

class AuthService {
  private refreshTimeout: ReturnType<typeof setTimeout> | null = null;

  async login(credentials: MemberAuthDTO): Promise<void> {
    const api = new AuthApi();
    const { data } = await api.loginAuthLoginPost(credentials);
    setCookie(REFRESH_TOKEN_COOKIE, data.refresh_token, { maxAge: REFRESH_TOKEN_MAX_AGE, path: '/', sameSite: 'Lax', secure: true });
    this.scheduleRefresh(data.access_token);
  }

  async logout(): Promise<void> {
    const refreshToken = getCookie(REFRESH_TOKEN_COOKIE);
    if (refreshToken) {
      const api = new AuthApi();
      await api.logoutAuthLogoutPost(refreshToken);
      deleteCookie(REFRESH_TOKEN_COOKIE);
    }
    if (this.refreshTimeout) 
        clearTimeout(this.refreshTimeout);
  }

  async refresh(): Promise<void> {
    const refreshToken = getCookie(REFRESH_TOKEN_COOKIE);
    if (!refreshToken) 
        throw new Error('No refresh token');
    const api = new AuthApi();
    const { data } = await api.refreshAuthRefreshPost(refreshToken);
    setCookie(REFRESH_TOKEN_COOKIE, data.refresh_token, { maxAge: REFRESH_TOKEN_MAX_AGE, path: '/', sameSite: 'Lax', secure: true });
    this.scheduleRefresh(data.access_token);
  }

  private scheduleRefresh(accessToken: string) {
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const exp = payload.exp * 1000; 
      const now = Date.now();
      const delay = Math.max(exp - now - 60 * 1000, 0); 
      if (this.refreshTimeout) clearTimeout(this.refreshTimeout);
      this.refreshTimeout = setTimeout(() => this.refresh(), delay);
    } catch (e) {
      if (this.refreshTimeout) clearTimeout(this.refreshTimeout);
      this.refreshTimeout = setTimeout(() => this.refresh(), 29 * 60 * 1000);
    }
  }

  isAuthenticated(): boolean {
    return !!getCookie(REFRESH_TOKEN_COOKIE);
  }
}

export const authService = new AuthService();
