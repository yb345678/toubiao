"""Explicit backend server entrypoint.

This file is intentionally tiny so deployment tools can use:

    python server.py

or:

    uvicorn api:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from run import main


if __name__ == "__main__":
    main()
