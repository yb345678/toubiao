from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.skill2_qualification_matcher.main import run


def test_qualification_matcher_flags_missing_materials():
    parsed = {"key_info": {"评分权重": "商务30分，技术45分，价格25分"}}
    result = run(parsed, "skills/skill2_qualification_matcher/demo_qualification.csv")
    assert result["score"] >= 60
    assert result["checks"]


if __name__ == "__main__":
    test_qualification_matcher_flags_missing_materials()
    print("Skill2 test passed")
