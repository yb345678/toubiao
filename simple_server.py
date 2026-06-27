"""Standard-library fallback web server.

This server is used when FastAPI/uvicorn are unavailable. It serves the static
page and keeps the complete demo workflow available without extra web runtime
dependencies.
"""

from __future__ import annotations

import cgi
import json
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from router import generate_report
from utils import OUTPUT_DIR, ROOT_DIR, ensure_dirs, now_stamp, safe_filename


class DemoHandler(SimpleHTTPRequestHandler):
    """Serve static files plus local analysis endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR / "static"), **kwargs)

    def _send_json(self, payload, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json({"status": "ok", "service": "ai-bidding-agent-system-fallback"})
            return

        if parsed.path == "/api/demo":
            report = generate_report(
                str(ROOT_DIR / "demo_data" / "mock_tender.pdf"),
                str(ROOT_DIR / "demo_data" / "company_qualification.xlsx"),
            )
            self._send_json(report)
            return

        if parsed.path == "/download":
            target = Path(parse_qs(parsed.query).get("path", [""])[0]).resolve()
            if OUTPUT_DIR.resolve() in target.parents and target.exists():
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(target.name)}")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            self._send_json({"error": "file not found or download denied"}, 404)
            return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self._send_json({"error": "not found"}, 404)
            return

        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST"})
        tender = form["tender_pdf"] if "tender_pdf" in form else None
        qualification = form["qualification_file"] if "qualification_file" in form else None
        if tender is None or qualification is None:
            self._send_json({"error": "please upload tender_pdf and qualification_file"}, 400)
            return

        upload_dir = OUTPUT_DIR / f"fallback_upload_{now_stamp()}"
        upload_dir.mkdir(parents=True, exist_ok=True)

        tender_name = tender.filename or "tender.pdf"
        qualification_name = qualification.filename or "qualification.xlsx"
        tender_path = upload_dir / f"{safe_filename(tender_name)}{Path(tender_name).suffix or '.pdf'}"
        qualification_path = upload_dir / f"{safe_filename(qualification_name)}{Path(qualification_name).suffix or '.xlsx'}"

        with tender_path.open("wb") as handle:
            shutil.copyfileobj(tender.file, handle)
        with qualification_path.open("wb") as handle:
            shutil.copyfileobj(qualification.file, handle)

        report = generate_report(str(tender_path), str(qualification_path), str(upload_dir / "report"))
        self._send_json(report)


def serve(port: int = 8000, host: str = "127.0.0.1") -> None:
    ensure_dirs()
    server = ThreadingHTTPServer((host, port), DemoHandler)
    print(f"Fallback backend server started: http://{host}:{port}")
    print("Fallback stdlib server is active. Static page, upload demo, and /api/demo are available.")
    server.serve_forever()


if __name__ == "__main__":
    serve()
