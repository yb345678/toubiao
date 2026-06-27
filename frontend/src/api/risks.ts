import { apiRequest } from "./client";

export interface StoredRisk {
  id: string;
  project_id: string;
  analysis_id: string;
  level: string;
  category?: string | null;
  title: string;
  source_page?: number | null;
  original_text?: string | null;
  negative_impact?: string | null;
  mitigation?: string | null;
  status: string;
  created_at: string;
}

export function listStoredRisks(projectId: string) {
  return apiRequest<StoredRisk[]>(`/api/v1/projects/${projectId}/risks`);
}
