import { apiRequest } from "./client";

export interface HealthResponse {
  status?: string;
  service?: string;
  version?: string;
  [key: string]: unknown;
}

export function getSystemHealth() {
  return apiRequest<HealthResponse>("/health");
}
