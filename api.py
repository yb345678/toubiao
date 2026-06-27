"""FastAPI backend for the AI bidding multi-agent system.

This module exposes the real backend API:

- GET  /health
- GET  /api/demo
- POST /api/analyze
- GET  /download

The static frontend in ./static is mounted at "/".
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from router import generate_report
from utils import OUTPUT_DIR, ROOT_DIR, ensure_dirs, now_stamp, safe_filename


app = FastAPI(title="AI Bidding Multi-Agent System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Prepare runtime folders before serving requests."""

    ensure_dirs()


@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint used by local scripts and deployment platforms."""

    return {"status": "ok", "service": "ai-bidding-agent-system"}


@app.post("/api/analyze")
async def analyze(tender_pdf: UploadFile = File(...), qualification_file: UploadFile = File(...)) -> JSONResponse:
    """Run the complete multi-agent workflow for uploaded files."""

    ensure_dirs()
    upload_dir = OUTPUT_DIR / f"upload_{now_stamp()}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    pdf_suffix = Path(tender_pdf.filename or "").suffix or ".pdf"
    qualification_suffix = Path(qualification_file.filename or "").suffix or ".xlsx"
    pdf_path = upload_dir / f"{safe_filename(tender_pdf.filename or 'tender')}{pdf_suffix}"
    qualification_path = upload_dir / f"{safe_filename(qualification_file.filename or 'qualification')}{qualification_suffix}"

    with pdf_path.open("wb") as handle:
        shutil.copyfileobj(tender_pdf.file, handle)
    with qualification_path.open("wb") as handle:
        shutil.copyfileobj(qualification_file.file, handle)

    report = generate_report(str(pdf_path), str(qualification_path), str(upload_dir / "report"))
    return JSONResponse(report)


@app.get("/api/demo")
def demo() -> JSONResponse:
    """Run the bundled demo data without requiring browser upload."""

    report = generate_report(
        str(ROOT_DIR / "demo_data" / "mock_tender.pdf"),
        str(ROOT_DIR / "demo_data" / "company_qualification.xlsx"),
    )
    return JSONResponse(report)


@app.get("/download")
def download(path: str):
    """Download generated report files under the outputs directory."""

    target = Path(path).resolve()
    output_root = OUTPUT_DIR.resolve()
    if output_root not in target.parents and target != output_root:
        return JSONResponse({"error": "only files under outputs can be downloaded"}, status_code=403)
    if not target.exists() or not target.is_file():
        return JSONResponse({"error": "file not found"}, status_code=404)
    return FileResponse(str(target), filename=target.name)


app.mount("/", StaticFiles(directory=str(ROOT_DIR / "static"), html=True), name="static")
