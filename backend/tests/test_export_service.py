from pathlib import Path
from types import SimpleNamespace
from app.services.export_service import (
    export_all,
    export_proposal_markdown,
    export_proposal_word,
    export_qualification_excel,
    export_risk_pdf,
)


def test_export_files_are_created(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.export_service.settings.output_dir", str(tmp_path))
    project = SimpleNamespace(id="project-1", name="Demo Project")
    analysis = SimpleNamespace(
        id="analysis-1",
        project_id="project-1",
        final_report_json="""{
          "decision": {"recommendation": "bid"},
          "agents": {
            "qualification_matcher": {"score": 90, "overall_status": "qualified", "missing_materials": [], "improvement_tips": ["Add SLA proof"]},
            "risk_reviewer": {"summary": {"high": 0, "medium": 1, "low": 0}, "risks": [{"level": "medium", "title": "Cost risk", "source_page": 2, "negative_impact": "Cost increase", "mitigation": "Price it in"}]},
            "proposal_writer": {"markdown_draft": "# Proposal\\n\\nDemo draft"}
          }
        }""",
    )

    files = [
        export_qualification_excel(project, analysis),
        export_risk_pdf(project, analysis),
        export_proposal_markdown(project, analysis),
        export_proposal_word(project, analysis),
        export_all(project, analysis),
    ]

    assert all(Path(file).exists() for file in files)
    assert files[0].suffix == ".xlsx"
    assert files[1].suffix == ".pdf"
    assert files[2].suffix == ".md"
    assert files[3].suffix == ".docx"
    assert files[4].suffix == ".zip"
