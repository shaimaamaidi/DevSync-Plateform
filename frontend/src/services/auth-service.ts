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

//const REFRESH_TOKEN_COOKIE = 'refresh_token';
const REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

class AuthService {
  private refreshTimeout: ReturnType<typeof setTimeout> | null = null;

  async login(credentials: MemberAuthDTO): Promise<void> {
    const api = new AuthApi();
    const { data } = await api.loginAuthLoginPost(credentials);
    setRefreshTokenCookie(data.refresh_token);
    this.scheduleRefresh();
  }

  async logout(): Promise<void> {
    const refreshToken = getRefreshTokenCookie();
    if (refreshToken) {
      try {
        const api = new AuthApi();
        await api.logoutAuthLogoutPost(refreshToken);
      } catch (e) {
        // Optionally log or handle error
      }
      deleteRefreshTokenCookie();
    }
    if (this.refreshTimeout) 
        clearTimeout(this.refreshTimeout);
  }

  async refresh(): Promise<void> {
    const refreshToken = getRefreshTokenCookie();
    if (!refreshToken) 
        throw new Error('No refresh token');
    const api = new AuthApi();
    const { data } = await api.refreshAuthRefreshPost(refreshToken);
    setRefreshTokenCookie(data.refresh_token);
    this.scheduleRefresh();
  }

  private scheduleRefresh() {
    if (this.refreshTimeout) 
        clearTimeout(this.refreshTimeout);
    this.refreshTimeout = setTimeout(() => this.refresh(), 29 * 60 * 1000);
  }

  isAuthenticated(): boolean {
    return !!getRefreshTokenCookie();
  }
}

export const authService = new AuthService();
