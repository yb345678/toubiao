"""PDF parsing Skill.

This module is deliberately self-contained: Router only passes a file path in
and receives a dictionary out.  The agent tries text PDF parsing first, then
uses OCR hooks when possible, and finally falls back to plain text fixtures used
by the hackathon demo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from utils import find_evidence, first_match, split_pages


def _read_pdf_with_pdfplumber(pdf_path: Path) -> Dict[str, Any]:
    """Extract text and tables from a real PDF using pdfplumber."""

    import pdfplumber

    pages: List[Dict[str, Any]] = []
    tables: List[Dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            page_tables = page.extract_tables() or []
            tables.extend(
                {
                    "page": page_index,
                    "rows": table,
                    "text": "\n".join(" | ".join(str(cell or "") for cell in row) for row in table),
                }
                for table in page_tables
            )
            pages.append({"page": page_index, "text": text, "ocr_used": False})
    return {"pages": pages, "tables": tables}


def _read_scan_with_ocr(pdf_path: Path) -> Dict[str, Any]:
    """OCR hook for scanned PDFs.

    `pytesseract` itself is allowed by the dependency rules, while page image
    rendering usually requires an external binary.  To keep the demo local and
    lightweight, this function records OCR availability and returns an empty
    result when the machine lacks a PDF rasterizer.
    """

    try:
        import pytesseract  # noqa: F401
    except Exception as exc:
        return {"pages": [], "tables": [], "ocr_note": f"pytesseract不可用：{exc}"}

    return {
        "pages": [],
        "tables": [],
        "ocr_note": "已检测到pytesseract；当前轻量版未调用外部PDF转图片工具，可接入Poppler后启用扫描件OCR。",
    }


def _read_text_fallback(pdf_path: Path) -> Dict[str, Any]:
    """Read demo fixtures that may use .pdf extension but contain plain text."""

    raw = pdf_path.read_text(encoding="utf-8", errors="ignore")
    pages = split_pages(raw)
    return {"pages": [{"page": p["page"], "text": p["text"], "ocr_used": False} for p in pages], "tables": []}


def _extract_key_info(pages: List[Dict[str, Any]], tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract bidding fields by transparent keyword/regex rules."""

    full_text = "\n".join(page.get("text", "") for page in pages)
    table_text = "\n".join(table.get("text", "") for table in tables)
    searchable = f"{full_text}\n{table_text}"

    key_info = {
        "项目预算": first_match(searchable, [r"(?:项目预算|预算金额|最高限价)[：:\s]*([0-9,.]+万元?)"]),
        "截标时间": first_match(searchable, [r"(?:截标时间|投标截止时间)[：:\s]*([0-9年月日:\-\s]+)"]),
        "保证金": first_match(searchable, [r"(?:投标保证金|保证金)[：:\s]*([0-9,.]+万元?)"]),
        "人员设备资质": first_match(searchable, [r"(?:人员设备资质|人员要求|设备要求)[：:\s]*(.+?)(?:\n|。|；)"]),
        "废标条款": first_match(searchable, [r"(?:废标条款|否决投标条款)[：:\s]*(.+?)(?:\n|。|；)"]),
        "评分权重": first_match(searchable, [r"(?:评分权重|评分细则)[：:\s]*(.+?)(?:\n|。)"]),
    }

    evidence = {
        field: find_evidence(pages, [field, str(value).split("，")[0], str(value).split("；")[0]], limit=3)
        for field, value in key_info.items()
    }
    return {"key_info": key_info, "evidence": evidence, "full_text": full_text}


def run(pdf_path: str) -> Dict[str, Any]:
    """Run Skill1 and return structured tender data."""

    path = Path(pdf_path)
    result: Dict[str, Any]
    try:
        result = _read_pdf_with_pdfplumber(path)
        if not any(page.get("text") for page in result["pages"]):
            ocr_result = _read_scan_with_ocr(path)
            result = ocr_result if ocr_result["pages"] else result | {"ocr_note": ocr_result.get("ocr_note", "")}
    except Exception as exc:
        result = _read_text_fallback(path)
        result["parse_note"] = f"pdfplumber解析失败，已启用文本回退：{exc}"

    extracted = _extract_key_info(result.get("pages", []), result.get("tables", []))
    return {
        "agent": "Skill1 PDF文档解析Agent",
        "status": "success",
        "source_file": str(path),
        "page_count": len(result.get("pages", [])),
        "pages": result.get("pages", []),
        "tables": result.get("tables", []),
        **extracted,
        "notes": [value for value in [result.get("parse_note"), result.get("ocr_note")] if value],
    }
