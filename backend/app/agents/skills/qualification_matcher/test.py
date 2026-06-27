from pathlib import Path

from app.agents.skills.qualification_matcher.main import run


def test_qualification_matcher_csv():
    parsed = {"key_info": {"scoring_weights": "商务30分，技术45分，价格25分"}}
    fixture = Path(__file__).with_name("demo_data") / "company_qualification.csv"
    result = run(parsed, str(fixture))
    assert result["status"] == "success"
    assert result["score"] >= 80
    assert result["overall_status"] == "qualified"
