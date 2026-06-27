"""One-click local service launcher.

Run:
    python run.py

Environment variables:
    HOST=127.0.0.1
    PORT=8000
    FORCE_FALLBACK=1
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    force_fallback = os.environ.get("FORCE_FALLBACK", "").lower() in {"1", "true", "yes"}

    sys.path.insert(0, ".")

    if not force_fallback:
        try:
            import api  # noqa: F401
            import uvicorn

            print(f"FastAPI backend server: http://{host}:{port}")
            print("API docs: /docs | Health: /health | Demo: /api/demo")
            uvicorn.run("api:app", host=host, port=port, reload=False)
            return
        except Exception as exc:
            print(f"FastAPI server unavailable, switching to fallback server: {exc}")

    from simple_server import serve

    serve(port=port, host=host)


if __name__ == "__main__":
    main()
