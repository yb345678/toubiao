from pathlib import Path

from app.agents.skills.proposal_writer.main import run


def test_proposal_writer_outputs_markdown():
    parsed = {
        "key_info": {
            "project_name": "Smart Park O&M",
            "budget": "380万元",
            "deadline": "2026-07-18 09:30",
            "deposit": "5万元",
            "scoring_weights": "商务30分，技术45分，价格25分",
        }
    }
    qualification = {"score": 100, "overall_status": "qualified", "missing_materials": []}
    risk = {"summary": {"high": 1, "medium": 1, "low": 0}, "risks": [{"level": "high", "source_page": 2, "title": "Rejection risk", "mitigation": "Checklist review"}]}
    fixture = Path(__file__).parents[1] / "qualification_matcher" / "demo_data" / "company_qualification.csv"
    result = run(parsed, qualification, risk, str(fixture))
    assert result["status"] == "success"
    assert "# Bid Proposal Draft" in result["markdown_draft"]
    assert result["business_outline"]
    assert result["technical_outline"]
