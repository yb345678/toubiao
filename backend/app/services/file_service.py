from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import UploadFile
    from app.models.project import Project

from app.core.config import settings
from app.core.exceptions import FileFormatError, bad_request, not_found
from app.services.blob_service import delete_blob, is_blob_enabled, upload_blob
from app.utils.file_utils import unique_filename


ALLOWED_FILE_TYPES = {
    "tender_pdf": {".pdf", ".txt"},
    "qualification_excel": {".xlsx", ".xls", ".csv"},
    "other_material": {".pdf", ".doc", ".docx", ".xlsx", ".xls", ".csv", ".txt"},
}


def _project_upload_dir(project: "Project") -> Path:
    return Path(settings.upload_dir) / project.id


def validate_upload(file_type: str, upload: "UploadFile") -> str:
    if file_type not in ALLOWED_FILE_TYPES:
        raise FileFormatError(f"Unsupported file_type: {file_type}")
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in ALLOWED_FILE_TYPES[file_type]:
        allowed = ", ".join(sorted(ALLOWED_FILE_TYPES[file_type]))
        raise FileFormatError(f"Unsupported extension {suffix or '<none>'}; allowed: {allowed}")
    return suffix


def save_project_file(project: "Project", upload: "UploadFile", file_type: str) -> dict:
    suffix = validate_upload(file_type, upload)
    original_name = upload.filename or f"{file_type}{suffix}"
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    data = upload.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise FileFormatError(f"File too large; max size is {settings.max_upload_size_mb} MB")

    if is_blob_enabled():
        blob = upload_blob(project.id, file_type, original_name, data, upload.content_type)
        stored_path = blob["url"]
        file_url = blob["url"]
    else:
        base = _project_upload_dir(project)
        base.mkdir(parents=True, exist_ok=True)
        target = base / unique_filename(file_type, original_name)
        target.write_bytes(data)
        stored_path = str(target)
        file_url = None

    return {
        "file_type": file_type,
        "original_name": upload.filename,
        "stored_path": stored_path,
        "file_url": file_url,
        "size": len(data),
        "content_type": upload.content_type,
    }


def apply_project_file(project: "Project", saved: dict) -> None:
    file_type = saved["file_type"]
    if file_type == "tender_pdf":
        project.tender_pdf_path = saved["stored_path"]
        project.tender_file_url = saved.get("file_url") or saved["stored_path"]
        project.tender_file_name = saved.get("original_name")
        project.tender_file_size = saved.get("size")
        project.tender_file_content_type = saved.get("content_type")
    elif file_type == "qualification_excel":
        project.qualification_file_path = saved["stored_path"]
        project.qualification_file_url = saved.get("file_url") or saved["stored_path"]
        project.qualification_file_name = saved.get("original_name")
        project.qualification_file_size = saved.get("size")
        project.qualification_file_content_type = saved.get("content_type")
    project.status = "uploaded" if project_files_ready(project) else "partial_uploaded"


def project_files_ready(project: "Project") -> bool:
    return bool(project.tender_file_url and project.qualification_file_url)


def missing_required_files(project: "Project") -> list[str]:
    missing: list[str] = []
    if not project.tender_file_url:
        missing.append("招标 PDF")
    if not project.qualification_file_url:
        missing.append("企业资质台账")
    return missing


def list_project_files(project: "Project") -> list[dict]:
    items: list[dict] = []
    mapping = {
        "tender_pdf": {
            "url": project.tender_file_url or project.tender_pdf_path,
            "name": project.tender_file_name,
            "size": project.tender_file_size,
            "content_type": project.tender_file_content_type,
        },
        "qualification_excel": {
            "url": project.qualification_file_url or project.qualification_file_path,
            "name": project.qualification_file_name,
            "size": project.qualification_file_size,
            "content_type": project.qualification_file_content_type,
        },
    }
    for file_type, info in mapping.items():
        stored_path = info["url"]
        if stored_path:
            path = Path(str(stored_path))
            items.append(
                {
                    "file_type": file_type,
                    "original_name": info["name"] or path.name,
                    "stored_path": str(stored_path),
                    "file_url": str(stored_path) if str(stored_path).startswith("http") else None,
                    "size": info["size"] or (path.stat().st_size if path.exists() else 0),
                    "content_type": info["content_type"],
                }
            )
    material_dir = _project_upload_dir(project)
    if material_dir.exists():
        for path in material_dir.glob("other_material_*"):
            items.append(
                {
                    "file_type": "other_material",
                    "original_name": path.name,
                    "stored_path": str(path),
                    "size": path.stat().st_size,
                    "content_type": None,
                }
            )
    return items


def get_project_file_path(project: "Project", file_type: str) -> Path:
    if file_type == "tender_pdf" and project.tender_pdf_path:
        return Path(project.tender_pdf_path)
    if file_type == "qualification_excel" and project.qualification_file_path:
        return Path(project.qualification_file_path)
    raise not_found("File not found")


def get_project_file_url(project: "Project", file_type: str) -> str:
    if file_type == "tender_pdf":
        url = project.tender_file_url or project.tender_pdf_path
    elif file_type == "qualification_excel":
        url = project.qualification_file_url or project.qualification_file_path
    else:
        url = None
    if not url:
        raise not_found("File not found")
    return url


def delete_project_file(project: "Project", file_type: str) -> None:
    if file_type == "tender_pdf":
        if project.tender_file_url:
            delete_blob(project.tender_file_url)
        elif project.tender_pdf_path:
            Path(project.tender_pdf_path).unlink(missing_ok=True)
        project.tender_pdf_path = None
        project.tender_file_url = None
        project.tender_file_name = None
        project.tender_file_size = None
        project.tender_file_content_type = None
    if file_type == "qualification_excel":
        if project.qualification_file_url:
            delete_blob(project.qualification_file_url)
        elif project.qualification_file_path:
            Path(project.qualification_file_path).unlink(missing_ok=True)
        project.qualification_file_path = None
        project.qualification_file_url = None
        project.qualification_file_name = None
        project.qualification_file_size = None
        project.qualification_file_content_type = None
    project.status = "uploaded" if project_files_ready(project) else "partial_uploaded"
