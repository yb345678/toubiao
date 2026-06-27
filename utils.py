"""Common local utilities for the AI bidding multi-agent demo.

The project intentionally keeps dependencies small.  Anything that can be
done with the Python standard library stays here so each Skill remains focused
on its own business logic.
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "outputs"
DEMO_DIR = ROOT_DIR / "demo_data"


def ensure_dirs() -> None:
    """Create folders used during local demos."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    DEMO_DIR.mkdir(exist_ok=True)


def now_stamp() -> str:
    """Return a filesystem-friendly timestamp."""

    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_filename(name: str) -> str:
    """Normalize filenames received from browsers."""

    stem = Path(name or "upload").stem
    clean = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "_", stem).strip("_")
    return clean or "upload"


def split_pages(text: str) -> List[Dict[str, Any]]:
    """Split demo text into page records.

    Real PDF extraction in Skill1 returns page records directly.  This helper is
    used by fallback paths and tests where the "PDF" may be a plain text fixture.
    """

    if not text:
        return [{"page": 1, "text": ""}]

    markers = list(re.finditer(r"(?:^|\n)\s*---\s*PAGE\s*(\d+)\s*---\s*(?:\n|$)", text, flags=re.I))
    if not markers:
        return [{"page": 1, "text": text.strip()}]

    pages: List[Dict[str, Any]] = []
    for index, marker in enumerate(markers):
        start = marker.end()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        pages.append({"page": int(marker.group(1)), "text": text[start:end].strip()})
    return pages or [{"page": 1, "text": text.strip()}]


def find_evidence(pages: Iterable[Dict[str, Any]], keywords: Iterable[str], limit: int = 5) -> List[Dict[str, Any]]:
    """Find source snippets by keyword and attach page numbers."""

    hits: List[Dict[str, Any]] = []
    keyword_list = [k for k in keywords if k]
    for page in pages:
        page_text = str(page.get("text", ""))
        normalized = re.sub(r"\s+", " ", page_text)
        for keyword in keyword_list:
            pos = normalized.find(keyword)
            if pos >= 0:
                left = max(0, pos - 45)
                right = min(len(normalized), pos + len(keyword) + 80)
                hits.append(
                    {
                        "page": page.get("page", 1),
                        "keyword": keyword,
                        "quote": normalized[left:right].strip(),
                    }
                )
                break
        if len(hits) >= limit:
            break
    return hits


def first_match(text: str, patterns: Iterable[str], default: str = "未识别") -> str:
    """Return the first regex capture group found in text."""

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.S)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" ：:\n\t")
    return default


def write_json(path: Path, data: Dict[str, Any]) -> None:
    """Write UTF-8 JSON with readable indentation."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown_doc(path: Path, title: str, body: str) -> None:
    """Write a Markdown document that opens cleanly in Word/WPS."""

    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"# {title}\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")


def write_csv_excel_fallback(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Create a CSV-compatible fallback when pandas/openpyxl are unavailable."""

    path.parent.mkdir(parents=True, exist_ok=True)
    columns = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_simple_pdf(path: Path, title: str, sections: List[Dict[str, str]]) -> None:
    """Write a small text PDF without external packages.

    The PDF uses Helvetica and ASCII-safe escaped text.  Chinese text is
    transliterated as UTF-8 bytes escaped into a simple stream; most viewers will
    still open it, while the Markdown/JSON reports keep full Chinese fidelity.
    This is sufficient for local demo export under the strict dependency list.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = [title, f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}", ""]
    for section in sections:
        lines.append(section.get("heading", "Section"))
        lines.extend(textwrap.wrap(section.get("body", ""), width=88) or [""])
        lines.append("")

    escaped_lines = []
    y = 780
    for line in lines[:54]:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        safe = safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        escaped_lines.append(f"BT /F1 10 Tf 50 {y} Td ({safe}) Tj ET")
        y -= 14

    stream = "\n".join(escaped_lines).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    offsets = [0]
    pdf = bytearray(b"%PDF-1.4\n")
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    path.write_bytes(bytes(pdf))


def html_escape(value: Any) -> str:
    """Escape arbitrary values for the static demo page."""

    return html.escape(str(value), quote=True)
