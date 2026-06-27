from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.file import ProjectFileList, ProjectFileRead
from app.services.file_service import delete_project_file, get_project_file_path, list_project_files, save_project_file
from app.services.persistence_service import record_history, record_log
from app.services.project_service import get_project_for_user


router = APIRouter()


@router.post("/{project_id}/files", response_model=ProjectFileRead)
def upload_project_file(
    project_id: str,
    file_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project_for_user(db, current_user, project_id)
    saved = save_project_file(project, file, file_type)
    if file_type == "tender_pdf":
        project.tender_pdf_path = saved["stored_path"]
    elif file_type == "qualification_excel":
        project.qualification_file_path = saved["stored_path"]
    project.status = "uploaded"
    record_history(
        db,
        user=current_user,
        project=project,
        action="file_uploaded",
        target_type="file",
        target_id=file_type,
        description=f"Uploaded {file_type}: {saved.get('original_name')}",
        after=saved,
    )
    record_log(
        db,
        user=current_user,
        project=project,
        module="files",
        event="file_uploaded",
        message=f"Uploaded {file_type}: {saved.get('original_name')}",
        metadata=saved,
    )
    db.commit()
    return ProjectFileRead(**saved)


@router.get("/{project_id}/files", response_model=ProjectFileList)
def list_project_file_api(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_for_user(db, current_user, project_id)
    return ProjectFileList(items=[ProjectFileRead(**item) for item in list_project_files(project)])


@router.get("/{project_id}/files/{file_type}/download")
def download_project_file(project_id: str, file_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_for_user(db, current_user, project_id)
    path = get_project_file_path(project, file_type)
    return FileResponse(str(path), filename=path.name)


@router.delete("/{project_id}/files/{file_type}")
def delete_project_file_api(project_id: str, file_type: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = get_project_for_user(db, current_user, project_id)
    delete_project_file(project, file_type)
    if not project.tender_pdf_path and not project.qualification_file_path:
        project.status = "draft"
    record_history(
        db,
        user=current_user,
        project=project,
        action="file_deleted",
        target_type="file",
        target_id=file_type,
        description=f"Deleted {file_type}",
    )
    db.commit()
    return {"message": "file deleted", "file_type": file_type}
