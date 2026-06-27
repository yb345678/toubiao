from pathlib import Path
from types import SimpleNamespace

from app.agents.skills.pdf_parser.main import run as parse_pdf
from app.agents.skills.qualification_matcher.main import run as match_qualification
from app.core.exceptions import ExcelReadError, FileFormatError, OCRProcessingError
from app.services.file_service import validate_upload


def test_file_format_error_for_invalid_pdf_extension():
    upload = SimpleNamespace(filename="bad.exe")
    try:
        validate_upload("tender_pdf", upload)
    except FileFormatError as exc:
        assert exc.code == "FILE_FORMAT_ERROR"
    else:
        raise AssertionError("FileFormatError expected")


def test_pdf_parser_reports_missing_file():
    try:
        parse_pdf("missing.pdf")
    except OCRProcessingError as exc:
        assert exc.code == "OCR_FAILED"
    else:
        raise AssertionError("OCRProcessingError expected")


def test_excel_reader_reports_missing_file():
    try:
        match_qualification({}, "missing.xlsx")
    except ExcelReadError as exc:
        assert exc.code == "EXCEL_READ_FAILED"
    else:
        raise AssertionError("ExcelReadError expected")
