from pathlib import Path

from app.agents.skills.pdf_parser.main import run


def test_pdf_parser_text_fallback():
    fixture = Path(__file__).with_name("demo_data") / "sample_tender.txt"
    result = run(str(fixture))
    assert result["status"] == "success"
    assert result["page_count"] == 2
    assert result["key_info"]["budget"] == "380万元"
    assert result["evidence"]
