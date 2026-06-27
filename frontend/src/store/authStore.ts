import type { UserRead } from "../api/auth";

export const TOKEN_KEY = "access_token";
export const REFRESH_TOKEN_KEY = "refresh_token";
export const CURRENT_USER_KEY = "current_user";

const LEGACY_TOKEN_KEYS = ["token", "jwt", "auth_token", "authToken", "accessToken"];
const LEGACY_REFRESH_TOKEN_KEYS = ["refreshToken"];

export function getToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) return token;

  for (const key of LEGACY_TOKEN_KEYS) {
    const legacyToken = localStorage.getItem(key);
    if (legacyToken) {
      localStorage.setItem(TOKEN_KEY, legacyToken);
      localStorage.removeItem(key);
      return legacyToken;
    }
  }

  return null;
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getRefreshToken() {
  const token = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (token) return token;

  for (const key of LEGACY_REFRESH_TOKEN_KEYS) {
    const legacyToken = localStorage.getItem(key);
    if (legacyToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, legacyToken);
      localStorage.removeItem(key);
      return legacyToken;
    }
  }

  return null;
}

export function setRefreshToken(token: string) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function setAuthTokens(accessToken: string, refreshToken: string) {
  setToken(accessToken);
  setRefreshToken(refreshToken);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(CURRENT_USER_KEY);
  for (const key of [...LEGACY_TOKEN_KEYS, ...LEGACY_REFRESH_TOKEN_KEYS]) {
    localStorage.removeItem(key);
  }
}

export function isAuthenticated() {
  return Boolean(getToken());
}

export function setCachedUser(user: UserRead) {
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
}

export function getCachedUser(): UserRead | null {
  const raw = localStorage.getItem(CURRENT_USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserRead;
  } catch {
    return null;
  }
}
