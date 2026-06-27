from io import BytesIO

from fastapi import UploadFile

from app.models.project import Project
from app.services.file_service import save_project_file


def test_save_project_file(tmp_path, monkeypatch):
    from app.core import config

    monkeypatch.setattr(config.settings, "upload_dir", str(tmp_path))
    project = Project(id="project-1", enterprise_id="enterprise-1", created_by="user-1", name="Demo")
    upload = UploadFile(filename="tender.pdf", file=BytesIO(b"demo pdf"))
    result = save_project_file(project, upload, "tender_pdf")
    assert result["size"] == 8
    assert result["stored_path"].endswith("tender_pdf_tender.pdf")
