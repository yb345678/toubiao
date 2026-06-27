from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from openpyxl import Workbook

from app.core.config import settings
from app.utils.file_utils import safe_filename


def _output_dir(project: Any, analysis: Any) -> Path:
    path = Path(settings.output_dir) / project.id / analysis.id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report(analysis: Any) -> dict:
    return json.loads(analysis.final_report_json or "{}")


def _proposal_text(analysis: Any) -> str:
    report = _report(analysis)
    proposal = report.get("agents", {}).get("proposal_writer", {})
    return proposal.get("markdown_draft") or "# Bid Proposal Draft\n\nNo proposal draft available."


def export_qualification_excel(project: Any, analysis: Any) -> Path:
    report = _report(analysis)
    qualification = report.get("agents", {}).get("qualification_matcher", {})
    output = _output_dir(project, analysis) / "qualification_match_result.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Qualification Match"
    rows = [
        ("Project", project.name),
        ("Score", qualification.get("score", "")),
        ("Overall Status", qualification.get("overall_status", "")),
        ("Recommendation", report.get("decision", {}).get("recommendation", "")),
    ]
    for row in rows:
        ws.append(row)

    ws.append([])
    ws.append(["Missing Materials"])
    for item in qualification.get("missing_materials", []) or []:
        ws.append([item])

    ws.append([])
    ws.append(["Improvement Tips"])
    for item in qualification.get("improvement_tips", qualification.get("bonus_tips", [])) or []:
        ws.append([item])

    ws.append([])
    ws.append(["Raw Qualification Result"])
    ws.append([json.dumps(qualification, ensure_ascii=False)])
    wb.save(output)
    return output


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_simple_pdf(path: Path, title: str, lines: list[str]) -> None:
    safe_lines = [title, ""] + [line[:100] for line in lines]
    y = 780
    stream_lines = ["BT", "/F1 12 Tf"]
    for line in safe_lines[:45]:
        stream_lines.append(f"50 {y} Td ({_pdf_escape(line)}) Tj")
        y = -16
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{index} 0 obj\n".encode())
        content.extend(obj)
        content.extend(b"\nendobj\n")
    xref_offset = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode())
    content.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode())
    path.write_bytes(content)


def export_risk_pdf(project: Any, analysis: Any) -> Path:
    report = _report(analysis)
    risk_result = report.get("agents", {}).get("risk_reviewer", {})
    output = _output_dir(project, analysis) / "risk_review_report.pdf"
    lines = [
        f"Project: {project.name}",
        f"Analysis: {analysis.id}",
        f"Summary: {risk_result.get('summary', {})}",
        "",
    ]
    for risk in risk_result.get("risks", [])[:20]:
        lines.extend(
            [
                f"[{risk.get('level')}] {risk.get('title')}",
                f"Page: {risk.get('source_page')}",
                f"Impact: {risk.get('negative_impact')}",
                f"Mitigation: {risk.get('mitigation')}",
                "",
            ]
        )
    _write_simple_pdf(output, "Bid Risk Review Report", lines)
    return output


def export_proposal_markdown(project: Any, analysis: Any) -> Path:
    output = _output_dir(project, analysis) / "bid_proposal_draft.md"
    output.write_text(_proposal_text(analysis), encoding="utf-8")
    return output


def export_proposal_word(project: Any, analysis: Any) -> Path:
    output = _output_dir(project, analysis) / "bid_proposal_draft.docx"
    paragraphs = _proposal_text(analysis).splitlines()
    document_xml = "".join(
        f"<w:p><w:r><w:t>{escape(line) if line else ' '}</w:t></w:r></w:p>" for line in paragraphs
    )
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        docx.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        docx.writestr("word/document.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>{document_xml}</w:body>
</w:document>""")
    return output


def export_all(project: Any, analysis: Any) -> Path:
    output_dir = _output_dir(project, analysis)
    files = [
        export_qualification_excel(project, analysis),
        export_risk_pdf(project, analysis),
        export_proposal_markdown(project, analysis),
        export_proposal_word(project, analysis),
    ]
    zip_path = output_dir / f"{safe_filename(project.name)}_export_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, file.name)
    return zip_path
