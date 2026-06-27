import { apiRequest } from "./client";

export interface StoredProposal {
  id: string;
  project_id: string;
  analysis_id: string;
  title: string;
  business_outline_json?: string | null;
  technical_outline_json?: string | null;
  matched_materials_json?: string | null;
  markdown_content?: string | null;
  file_path?: string | null;
  version: number;
  status: string;
  created_at: string;
}

export function listStoredProposals(projectId: string) {
  return apiRequest<StoredProposal[]>(`/api/v1/projects/${projectId}/proposals`);
}

export function getLatestStoredProposal(projectId: string) {
  return apiRequest<StoredProposal>(`/api/v1/projects/${projectId}/proposals/latest`);
}
