from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.skill1_pdf_parser.main import run as parse
from skills.skill3_risk_reviewer.main import run


def test_risk_reviewer_finds_rejection_clause():
    parsed = parse(str(Path("skills/skill1_pdf_parser/demo_tender.txt")))
    result = run(parsed)
    assert result["summary"]["高风险"] >= 1


if __name__ == "__main__":
    test_risk_reviewer_finds_rejection_clause()
    print("Skill3 test passed")
