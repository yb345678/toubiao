"""Skill1: PDF document parser agent."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from app.agents.skills.pdf_parser.schema import (
    EvidenceItem,
    PDFParserInput,
    PDFParserOutput,
    PageText,
    ParsedKeyInfo,
    TableData,
)
from app.core.exceptions import OCRProcessingError


def _read_with_pdfplumber(path: Path) -> tuple[list[PageText], list[TableData]]:
    import pdfplumber

    pages: list[PageText] = []
    tables: list[TableData] = []
    with pdfplumber.open(str(path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(PageText(page_number=page_number, text=text, ocr_used=False))
            for table in page.extract_tables() or []:
                table_text = "\n".join(" | ".join(str(cell or "") for cell in row) for row in table)
                tables.append(TableData(page_number=page_number, rows=table, text=table_text))
    return pages, tables


def _read_text_fallback(path: Path) -> list[PageText]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    markers = list(re.finditer(r"(?:^|\n)\s*---\s*PAGE\s*(\d+)\s*---\s*(?:\n|$)", text, flags=re.I))
    if not markers:
        return [PageText(page_number=1, text=text.strip(), ocr_used=False)]

    pages: list[PageText] = []
    for index, marker in enumerate(markers):
        start = marker.end()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        pages.append(PageText(page_number=int(marker.group(1)), text=text[start:end].strip(), ocr_used=False))
    return pages


def _first_match(text: str, patterns: Iterable[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I | re.S)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" ：:\n\t")
    return None


def _find_evidence(pages: list[PageText], field: str, keywords: Iterable[str], limit: int = 3) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for page in pages:
        normalized = re.sub(r"\s+", " ", page.text)
        for keyword in [k for k in keywords if k]:
            pos = normalized.find(keyword)
            if pos >= 0:
                left = max(0, pos - 45)
                right = min(len(normalized), pos + len(keyword) + 90)
                items.append(
                    EvidenceItem(
                        field=field,
                        page_number=page.page_number,
                        keyword=keyword,
                        quote=normalized[left:right].strip(),
                    )
                )
                break
        if len(items) >= limit:
            break
    return items


def _extract_key_info(pages: list[PageText], tables: list[TableData]) -> tuple[ParsedKeyInfo, list[EvidenceItem]]:
    full_text = "\n".join(page.text for page in pages)
    table_text = "\n".join(table.text for table in tables)
    searchable = f"{full_text}\n{table_text}"

    key_info = ParsedKeyInfo(
        project_name=_first_match(searchable, [r"(?:项目名称|招标项目名称|项目)[：:\s]*([^\n。；]+)"]),
        budget=_first_match(searchable, [r"(?:项目预算|预算金额|最高限价)[：:\s]*([0-9,.]+万元?)"]),
        deadline=_first_match(searchable, [r"(?:截标时间|投标截止时间|递交截止时间)[：:\s]*([0-9年月日:\-\s]+)"]),
        deposit=_first_match(searchable, [r"(?:投标保证金|保证金)[：:\s]*([0-9,.]+万元?)"]),
        qualification_requirements=_first_match(searchable, [r"(?:人员设备资质|人员要求|资格要求|资质要求)[：:\s]*(.+?)(?:\n|。|；)"]),
        rejection_clauses=_first_match(searchable, [r"(?:废标条款|否决投标条款|无效投标)[：:\s]*(.+?)(?:\n|。|；)"]),
        scoring_weights=_first_match(searchable, [r"(?:评分权重|评分细则|评分办法)[：:\s]*(.+?)(?:\n|。)"]),
    )

    evidence: list[EvidenceItem] = []
    fields = key_info.model_dump()
    keyword_map = {
        "project_name": ["项目名称", fields.get("project_name")],
        "budget": ["项目预算", "预算金额", "最高限价", fields.get("budget")],
        "deadline": ["截标时间", "投标截止时间", fields.get("deadline")],
        "deposit": ["保证金", "投标保证金", fields.get("deposit")],
        "qualification_requirements": ["人员设备资质", "资格要求", "资质要求"],
        "rejection_clauses": ["废标条款", "否决投标", "无效投标"],
        "scoring_weights": ["评分权重", "评分细则", "评分办法"],
    }
    for field, keywords in keyword_map.items():
        evidence.extend(_find_evidence(pages, field, keywords))
    return key_info, evidence


def parse_pdf(payload: PDFParserInput) -> PDFParserOutput:
    path = Path(payload.pdf_path)
    if not path.exists():
        raise OCRProcessingError(f"PDF file not found: {path}")
    notes: list[str] = []
    tables: list[TableData] = []
    try:
        pages, tables = _read_with_pdfplumber(path)
        if not any(page.text for page in pages):
            notes.append("No text extracted by pdfplumber; OCR hook should be enabled for scanned PDFs.")
    except Exception as exc:
        try:
            pages = _read_text_fallback(path)
            notes.append(f"pdfplumber failed; text fallback enabled: {exc}")
        except Exception as fallback_exc:
            raise OCRProcessingError(f"PDF/OCR parsing failed: {fallback_exc}") from fallback_exc

    key_info, evidence = _extract_key_info(pages, tables)
    full_text = "\n".join(page.text for page in pages)
    return PDFParserOutput(
        source_file=str(path),
        page_count=len(pages),
        full_text=full_text,
        pages=pages,
        tables=tables,
        key_info=key_info,
        evidence=evidence,
        notes=notes,
    )


def run(pdf_path: str) -> dict:
    """Compatibility function for Router usage."""

    return parse_pdf(PDFParserInput(pdf_path=pdf_path)).model_dump()
