from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError


logger = logging.getLogger("ai_bidding")


def error_payload(code: str, message: str, request: Request) -> dict:
    return {
        "success": False,
        "code": code,
        "detail": message,
        "path": str(request.url.path),
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning("%s: %s", exc.code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message, request))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        message = str(exc.detail)
        return JSONResponse(status_code=exc.status_code, content=error_payload("HTTP_ERROR", message, request))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_payload("VALIDATION_ERROR", "Request validation failed", request) | {"errors": exc.errors()},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error")
        return JSONResponse(status_code=500, content=error_payload("DATABASE_ERROR", "Database operation failed", request))

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        logger.exception("Unexpected server error")
        return JSONResponse(status_code=500, content=error_payload("INTERNAL_ERROR", "Unexpected server error", request))
