from __future__ import annotations

import os
import shutil
from pathlib import Path

import requests
import vercel_blob

from app.core.config import settings
from app.core.exceptions import bad_request, not_found
from app.utils.file_utils import unique_filename


def is_blob_enabled() -> bool:
    return bool(settings.blob_read_write_token)


def _blob_options() -> dict:
    if not settings.blob_read_write_token:
        raise bad_request("BLOB_READ_WRITE_TOKEN is required for persistent file storage")
    return {"token": settings.blob_read_write_token}


def upload_blob(project_id: str, file_type: str, filename: str, data: bytes, content_type: str | None = None) -> dict:
    safe_name = unique_filename(file_type, filename)
    pathname = f"projects/{project_id}/{file_type}/{safe_name}"
    options = _blob_options() | {"addRandomSuffix": "false", "allowOverwrite": "true"}
    result = vercel_blob.put(pathname, data, options=options, timeout=60, verbose=False)
    url = result.get("url") or result.get("downloadUrl") or result.get("pathname")
    if not url:
        raise bad_request("Blob upload did not return a file URL")
    return result | {"url": url, "pathname": pathname}


def delete_blob(url: str | None) -> None:
    if not url or not settings.blob_read_write_token:
        return
    try:
        vercel_blob.delete(url, options=_blob_options(), timeout=30)
    except Exception:
        return


def download_url_to_tmp(url: str, suffix: str, prefix: str) -> Path:
    tmp_dir = Path("/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    target = tmp_dir / unique_filename(prefix, f"download{suffix or '.bin'}")
    if not url.startswith(("http://", "https://")):
        source = Path(url)
        if not source.exists():
            raise not_found("Stored file was not found on local storage")
        shutil.copyfile(source, target)
        return target
    response = requests.get(url, timeout=60)
    if response.status_code == 404:
        raise not_found("Stored file was not found in object storage")
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def remove_tmp_file(path: Path | str | None) -> None:
    if not path:
        return
    try:
        os.remove(path)
    except FileNotFoundError:
        return
