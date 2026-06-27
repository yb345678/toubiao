import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";
import { clearToken, getRefreshToken, getToken, setAuthTokens } from "../store/authStore";

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

const PUBLIC_PATHS = ["/health", "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/refresh"];

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  withCredentials: false
});

let refreshPromise: Promise<string> | null = null;

function requestPath(url?: string): string {
  if (!url) return "";
  if (url.startsWith("http")) {
    try {
      return new URL(url).pathname;
    } catch {
      return url;
    }
  }
  return url.split("?")[0];
}

function isPublicRequest(url?: string): boolean {
  const path = requestPath(url);
  return PUBLIC_PATHS.some((publicPath) => path === publicPath || path.startsWith(`${publicPath}?`));
}

function redirectToLogin() {
  if (typeof window === "undefined") return;
  const currentPath = `${window.location.pathname}${window.location.search}`;
  if (window.location.pathname === "/login") return;
  window.location.assign(`/login?next=${encodeURIComponent(currentPath)}`);
}

function authErrorMessage(data: unknown, fallback = "认证失败，请重新登录。") {
  const detail =
    typeof data === "string"
      ? data
      : typeof data === "object" && data && "detail" in data
        ? String((data as { detail?: unknown }).detail || "")
        : "";
  const normalized = detail.toLowerCase();

  if (normalized.includes("missing bearer")) return "未检测到登录凭证，请重新登录。";
  if (normalized.includes("malformed_token")) return "登录凭证格式错误，请重新登录。";
  if (normalized.includes("token_expired")) return "登录已过期，请重新登录。";
  if (normalized.includes("invalid_signature")) return "登录凭证验证失败，请重新登录。";
  if (normalized.includes("wrong_token_type")) return "登录凭证类型错误，请重新登录。";
  if (normalized.includes("user not found")) return "登录用户不存在或会话已失效，请重新登录。";
  if (normalized.includes("user is disabled")) return "账号已被停用，请联系管理员。";
  if (normalized.includes("invalid token")) return "登录凭证无效，请重新登录。";

  return fallback;
}

httpClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else if (!isPublicRequest(config.url)) {
    clearToken();
    redirectToLogin();
    throw new ApiError("请先登录后再继续操作。", 401);
  }
  return config;
});

httpClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (!error.response) {
      throw new ApiError(
        `无法连接后端服务${API_BASE_URL ? `：${API_BASE_URL}` : ""}。请检查 VITE_API_BASE_URL 或后端服务状态。`,
        0,
        error
      );
    }

    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isPublicRequest(originalRequest.url)
    ) {
      originalRequest._retry = true;
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          if (!refreshPromise) {
            refreshPromise = refreshAccessToken(refreshToken).finally(() => {
              refreshPromise = null;
            });
          }
          const newAccessToken = await refreshPromise;
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return httpClient.request(originalRequest);
        } catch (refreshError) {
          clearToken();
          redirectToLogin();
          if (axios.isAxiosError(refreshError)) {
            throw new ApiError(authErrorMessage(refreshError.response?.data), 401, refreshError.response?.data);
          }
          throw new ApiError("刷新登录状态失败，请重新登录。", 401, refreshError);
        }
      }
      clearToken();
      redirectToLogin();
      throw new ApiError(authErrorMessage(error.response.data), 401, error.response.data);
    }

    const data = error.response.data as { code?: string; detail?: string; error?: string; message?: string } | string | undefined;
    const message =
      typeof data === "string"
        ? data
        : [data?.code, data?.detail || data?.error || data?.message || `Request failed with status ${error.response.status}`]
            .filter(Boolean)
            .join(": ");

    throw new ApiError(message, error.response.status, error.response.data);
  }
);

async function refreshAccessToken(refreshToken: string): Promise<string> {
  const response = await axios.post<{
    access_token: string;
    refresh_token: string;
    expires_in: number;
    refresh_expires_in: number;
  }>(`${API_BASE_URL}/api/v1/auth/refresh`, {
    refresh_token: refreshToken
  });

  setAuthTokens(response.data.access_token, response.data.refresh_token);
  return response.data.access_token;
}

function normalizeConfig(options: RequestInit): AxiosRequestConfig {
  const headers = new Headers(options.headers);
  const config: AxiosRequestConfig = {
    method: options.method as AxiosRequestConfig["method"],
    data: options.body,
    headers: Object.fromEntries(headers.entries())
  };

  if (options.body instanceof FormData) {
    delete config.headers?.["content-type"];
    delete config.headers?.["Content-Type"];
  } else if (options.body && !config.headers?.["Content-Type"] && !config.headers?.["content-type"]) {
    config.headers = {
      ...config.headers,
      "Content-Type": "application/json"
    };
  }

  return config;
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await httpClient.request<T>({
    url: path,
    ...normalizeConfig(options)
  });

  return response.data;
}
