import { API_BASE_URL, apiRequest, httpClient } from "./client";

export type ProjectFileType = "tender_pdf" | "qualification_excel";

export interface ProjectFile {
  file_type: ProjectFileType | string;
  original_name?: string | null;
  stored_path: string;
  file_url?: string | null;
  size: number;
  content_type?: string | null;
}

export interface ProjectFileList {
  items: ProjectFile[];
}

export function listProjectFiles(projectId: string) {
  return apiRequest<ProjectFileList>(`/api/v1/projects/${projectId}/files`);
}

export function uploadProjectFile(
  projectId: string,
  fileType: ProjectFileType,
  file: File,
  onProgress?: (percent: number) => void
) {
  const formData = new FormData();
  formData.append("file_type", fileType);
  formData.append("file", file);

  return httpClient
    .post<ProjectFile>(`/api/v1/projects/${projectId}/files`, formData, {
      onUploadProgress: (event) => {
        if (!event.total) return;
        onProgress?.(Math.round((event.loaded / event.total) * 100));
      }
    })
    .then((response) => response.data);
}

export function deleteProjectFile(projectId: string, fileType: ProjectFileType) {
  return apiRequest<{ message: string; file_type: string }>(`/api/v1/projects/${projectId}/files/${fileType}`, {
    method: "DELETE"
  });
}

export function projectFileDownloadUrl(projectId: string, fileType: ProjectFileType) {
  return `${API_BASE_URL}/api/v1/projects/${projectId}/files/${fileType}/download`;
}
