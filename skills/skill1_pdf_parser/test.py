from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.skill1_pdf_parser.main import run


def test_pdf_parser_demo_fixture():
    fixture = Path(__file__).with_name("demo_tender.txt")
    result = run(str(fixture))
    assert result["status"] == "success"
    assert result["key_info"]["项目预算"] != "未识别"
    assert result["evidence"]["项目预算"][0]["page"] == 1


if __name__ == "__main__":
    test_pdf_parser_demo_fixture()
    print("Skill1 test passed")
