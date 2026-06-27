# Skill1 PDF Document Parser Agent

## Goal

Parse tender PDF documents and extract structured bidding information with
page-level evidence.

## Input

```json
{
  "pdf_path": "uploads/project/tender.pdf"
}
```

## Output

```json
{
  "agent": "pdf_parser",
  "status": "success",
  "page_count": 3,
  "full_text": "...",
  "pages": [],
  "tables": [],
  "key_info": {},
  "evidence": []
}
```

## Responsibilities

- Extract PDF text with `pdfplumber`.
- Extract table rows when available.
- Keep OCR hook for scanned PDFs through `pytesseract`.
- Extract tender budget, deadline, deposit, qualification requirements,
  rejection clauses, and scoring weights.
- Bind every key field to original page evidence.

## Boundaries

- This Skill does not access the database.
- This Skill does not call other Agents.
- This Skill returns plain dictionaries and Pydantic schemas.
