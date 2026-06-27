import { apiRequest } from "./client";

export interface AnalysisTask {
  id: string;
  project_id: string;
  status: "running" | "completed" | "failed" | string;
  progress: number;
  current_step?: string | null;
  score?: number | null;
  recommendation?: string | null;
  summary?: string | null;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface AnalysisStartResponse {
  task_id: string;
  status: string;
}

export interface ReportResponse {
  analysis_id: string;
  project_id: string;
  final_report: Record<string, unknown>;
}

export function startAnalysis(projectId: string) {
  return apiRequest<AnalysisStartResponse>(`/api/v1/projects/${projectId}/analysis/start`, {
    method: "POST"
  });
}

export function getAnalysisTask(analysisId: string) {
  return apiRequest<AnalysisTask>(`/api/v1/analysis-tasks/${analysisId}`);
}

export function getLatestReport(projectId: string) {
  return apiRequest<ReportResponse>(`/api/v1/projects/${projectId}/reports/latest`);
}
