import { API_BASE_URL, apiRequest } from "./client";
import type { ReportResponse } from "./analysis";

export function getReportByAnalysisId(analysisId: string) {
  return apiRequest<ReportResponse>(`/api/v1/reports/${analysisId}`);
}

export type ExportKind = "qualification-excel" | "risk-pdf" | "proposal-markdown" | "proposal-word" | "all";

export function exportUrl(projectId: string, kind: ExportKind) {
  return `${API_BASE_URL}/api/v1/projects/${projectId}/exports/${kind}`;
}

export function downloadExport(projectId: string, kind: ExportKind) {
  window.open(exportUrl(projectId, kind), "_blank", "noopener,noreferrer");
}
