"""Reserved async task runner.

The hackathon MVP runs analysis synchronously for simplicity. This module is the
future extension point for Celery/RQ/Arq or FastAPI BackgroundTasks.
"""

from __future__ import annotations


def enqueue_analysis(project_id: str) -> str:
    return project_id
