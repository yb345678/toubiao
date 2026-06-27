import { apiRequest } from "./client";

export interface DashboardSummary {
  project_count: number;
  completed_count: number;
  running_count: number;
  average_score?: number;
  high_risk_count?: number;
}

export function getDashboardSummary() {
  return apiRequest<DashboardSummary>("/api/v1/dashboard/summary");
}
