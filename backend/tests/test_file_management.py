from app.utils.file_utils import safe_filename, unique_filename


def test_unique_filename_prevents_overwrite():
    first = unique_filename("tender_pdf", "招标文件.pdf")
    second = unique_filename("tender_pdf", "招标文件.pdf")

    assert first != second
    assert first.startswith("tender_pdf_")
    assert first.endswith(".pdf")
    assert second.endswith(".pdf")


def test_safe_filename_keeps_basic_extension():
    assert safe_filename("../../demo tender.pdf").endswith(".pdf")
