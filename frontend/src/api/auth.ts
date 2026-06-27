import { apiRequest } from "./client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_expires_in: number;
}

export interface RefreshPayload {
  refresh_token: string;
}

export interface UserRead {
  id: string;
  email: string;
  username: string;
  role: string;
  status: string;
  created_at: string;
}

export function login(payload: LoginPayload) {
  return apiRequest<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function register(payload: RegisterPayload) {
  return apiRequest<UserRead>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getMe() {
  return apiRequest<UserRead>("/api/v1/auth/me");
}

export function refreshToken(payload: RefreshPayload) {
  return apiRequest<TokenResponse>("/api/v1/auth/refresh", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
