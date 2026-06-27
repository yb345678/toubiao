"""Application exception helpers."""

from __future__ import annotations

try:
    from fastapi import HTTPException, status
except ModuleNotFoundError:  # Allows Skill tests to run without FastAPI installed.
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class status:
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_404_NOT_FOUND = 404
        HTTP_422_UNPROCESSABLE_ENTITY = 422
        HTTP_500_INTERNAL_SERVER_ERROR = 500


class AppError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class FileFormatError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "FILE_FORMAT_ERROR", status.HTTP_400_BAD_REQUEST)


class OCRProcessingError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "OCR_FAILED", status.HTTP_422_UNPROCESSABLE_ENTITY)


class ExcelReadError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "EXCEL_READ_FAILED", status.HTTP_422_UNPROCESSABLE_ENTITY)


class AgentExecutionError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "AGENT_EXECUTION_FAILED", status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseError(AppError):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)


def not_found(message: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def unauthorized(message: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
