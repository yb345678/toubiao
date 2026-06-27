from pathlib import Path

from app.agents.orchestrator import run_analysis_workflow


def test_router_workflow_progress_and_report():
    steps = []

    def on_progress(step: str, progress: int):
        steps.append((step, progress))

    result = run_analysis_workflow(
        str(Path("../demo_data/mock_tender.pdf")),
        str(Path("../demo_data/company_qualification.xlsx")),
        progress_callback=on_progress,
    )

    assert result["decision"]["score"] >= 80
    assert result["agents"]["pdf_parser"]
    assert result["agent_runs"][0]["agent_name"] == "pdf_parser"
    assert [run["agent_name"] for run in result["agent_runs"]] == [
        "pdf_parser",
        "qualification_matcher",
        "risk_reviewer",
        "proposal_writer",
    ]
    assert [step[0] for step in steps if not step[0].endswith("_completed")][:4] == [
        "pdf_parser",
        "qualification_matcher",
        "risk_reviewer",
        "proposal_writer",
    ]
    assert result["workflow_steps"][0]["key"] == "pdf_parser"
    assert result["workflow_steps"][3]["key"] == "proposal_writer"
