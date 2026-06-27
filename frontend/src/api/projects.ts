import { apiRequest } from "./client";

export interface Enterprise {
  id: string;
  owner_user_id: string;
  name: string;
  credit_code?: string | null;
  industry?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  contact_email?: string | null;
  description?: string | null;
  status: string;
  created_at: string;
}

export interface Project {
  id: string;
  enterprise_id: string;
  created_by: string;
  name: string;
  tender_name?: string | null;
  tender_company?: string | null;
  status: string;
  latest_score?: number | null;
  latest_recommendation?: string | null;
  created_at: string;
}

export interface CreateEnterprisePayload {
  name: string;
  credit_code?: string;
  industry?: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
  description?: string;
}

export interface CreateProjectPayload {
  enterprise_id: string;
  name: string;
  tender_name?: string;
  tender_company?: string;
}

export function listEnterprises() {
  return apiRequest<Enterprise[]>("/api/v1/projects/enterprises");
}

export function createEnterprise(payload: CreateEnterprisePayload) {
  return apiRequest<Enterprise>("/api/v1/projects/enterprises", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listProjects() {
  return apiRequest<Project[]>("/api/v1/projects");
}

export function createProject(payload: CreateProjectPayload) {
  return apiRequest<Project>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
