from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path


def safe_filename(name: str) -> str:
    clean = re.sub(r"[^0-9A-Za-z_.\-\u4e00-\u9fff]+", "_", name or "file")
    return clean.strip("_") or "file"


def unique_filename(file_type: str, original_name: str) -> str:
    safe = safe_filename(original_name)
    path = Path(safe)
    stem = safe_filename(path.stem) or file_type
    suffix = path.suffix.lower()
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    return f"{file_type}_{stamp}_{short_id}_{stem}{suffix}"
