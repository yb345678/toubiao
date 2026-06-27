from __future__ import annotations

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Page(BaseModel):
    items: list
    total: int
    page: int = 1
    page_size: int = 20
