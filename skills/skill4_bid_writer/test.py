from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from skills.skill4_bid_writer.main import run


def test_bid_writer_outputs_markdown():
    parsed = {"key_info": {"项目预算": "380万元", "评分权重": "商务30分，技术45分，价格25分"}}
    match = {"score": 92, "missing_materials": []}
    result = run(parsed, match, "skills/skill2_qualification_matcher/demo_qualification.csv")
    assert "## 三、技术标应答" in result["markdown_draft"]


if __name__ == "__main__":
    test_bid_writer_outputs_markdown()
    print("Skill4 test passed")
