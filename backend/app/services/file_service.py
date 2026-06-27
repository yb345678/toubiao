from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import UploadFile
    from app.models.project import Project

from app.core.config import settings
from app.core.exceptions import FileFormatError, bad_request, not_found
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
    base = _project_upload_dir(project)
    base.mkdir(parents=True, exist_ok=True)

    original_name = upload.filename or f"{file_type}{suffix}"
    target = base / unique_filename(file_type, original_name)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    written = 0

    with target.open("wb") as handle:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                handle.close()
                target.unlink(missing_ok=True)
                raise FileFormatError(f"File too large; max size is {settings.max_upload_size_mb} MB")
            handle.write(chunk)

    return {
        "file_type": file_type,
        "original_name": upload.filename,
        "stored_path": str(target),
        "size": written,
        "content_type": upload.content_type,
    }


def list_project_files(project: "Project") -> list[dict]:
    items: list[dict] = []
    mapping = {
        "tender_pdf": project.tender_pdf_path,
        "qualification_excel": project.qualification_file_path,
    }
    for file_type, stored_path in mapping.items():
        if stored_path:
            path = Path(stored_path)
            items.append(
                {
                    "file_type": file_type,
                    "original_name": path.name,
                    "stored_path": str(path),
                    "size": path.stat().st_size if path.exists() else 0,
                    "content_type": None,
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


def delete_project_file(project: "Project", file_type: str) -> None:
    path = get_project_file_path(project, file_type)
    path.unlink(missing_ok=True)
    if file_type == "tender_pdf":
        project.tender_pdf_path = None
    if file_type == "qualification_excel":
        project.qualification_file_path = None
