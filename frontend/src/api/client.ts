import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

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

httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
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
      originalRequest.url !== "/api/v1/auth/login" &&
      originalRequest.url !== "/api/v1/auth/refresh"
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
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
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          localStorage.removeItem("current_user");
        }
      }
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

  localStorage.setItem("access_token", response.data.access_token);
  localStorage.setItem("refresh_token", response.data.refresh_token);
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
