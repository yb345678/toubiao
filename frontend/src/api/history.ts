import { apiRequest } from "./client";

export interface HistoryRecord {
  id: string;
  user_id?: string | null;
  project_id?: string | null;
  analysis_id?: string | null;
  action: string;
  target_type?: string | null;
  target_id?: string | null;
  description?: string | null;
  created_at: string;
}

export function listHistoryRecords() {
  return apiRequest<HistoryRecord[]>("/api/v1/history");
}
