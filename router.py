"""Multi-agent Router for the AI bidding workflow.

Router is the only orchestration layer.  It does not contain Skill-specific
business rules; it only passes context between independent agents and exports
the final materials required by the local demo.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from skills.skill1_pdf_parser.main import run as parse_pdf
from skills.skill2_qualification_matcher.main import run as match_qualification
from skills.skill3_risk_reviewer.main import run as review_risk
from skills.skill4_bid_writer.main import run as write_bid
from utils import OUTPUT_DIR, ensure_dirs, now_stamp, safe_filename, write_json, write_markdown_doc, write_simple_pdf


def _export_score_excel(match_result: Dict[str, Any], output_dir: Path) -> Path:
    """Export qualification scoring result to Excel, falling back to CSV."""

    rows = match_result.get("checks", [])
    xlsx_path = output_dir / "资质匹配打分.xlsx"
    try:
        import pandas as pd

        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            pd.DataFrame(rows).to_excel(writer, index=False, sheet_name="逐条校验")
            pd.DataFrame(
                [
                    {
                        "综合得分": match_result.get("score"),
                        "总体状态": match_result.get("overall_status"),
                        "缺失材料": "；".join(match_result.get("missing_materials", [])),
                    }
                ]
            ).to_excel(writer, index=False, sheet_name="汇总")
        return xlsx_path
    except Exception:
        csv_path = output_dir / "资质匹配打分.csv"
        from utils import write_csv_excel_fallback

        write_csv_excel_fallback(csv_path, rows)
        return csv_path


def _export_risk_pdf(risk_result: Dict[str, Any], output_dir: Path) -> Path:
    """Export risk review report to a local PDF file."""

    sections = []
    for risk in risk_result.get("risks", []):
        sections.append(
            {
                "heading": f"{risk.get('level')} | 第{risk.get('source_page')}页",
                "body": f"依据：{risk.get('original_text')} 影响：{risk.get('negative_impact')} 应对：{risk.get('mitigation')}",
            }
        )
    path = output_dir / "风险审查PDF报告.pdf"
    write_simple_pdf(path, "投标风险审查报告", sections)
    return path


def _export_bid_doc(bid_result: Dict[str, Any], output_dir: Path) -> Path:
    """Export editable bid proposal draft."""

    path = output_dir / "投标方案Markdown初稿.md"
    write_markdown_doc(path, "投标方案初稿", bid_result.get("markdown_draft", ""))
    return path


def generate_report(pdf_path: str, qualification_path: str, output_base: str | None = None) -> Dict[str, Any]:
    """Run the complete upload-to-report multi-agent workflow."""

    ensure_dirs()
    base_name = safe_filename(Path(pdf_path).name)
    output_dir = Path(output_base) if output_base else OUTPUT_DIR / f"{now_stamp()}_{base_name}"
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_pdf(pdf_path)
    matched = match_qualification(parsed, qualification_path)
    risks = review_risk(parsed)
    bid = write_bid(parsed, matched, qualification_path)

    exports = {
        "qualification_excel": str(_export_score_excel(matched, output_dir)),
        "risk_pdf": str(_export_risk_pdf(risks, output_dir)),
        "bid_document": str(_export_bid_doc(bid, output_dir)),
    }

    report = {
        "project": "AI招投标多智能体系统",
        "workflow": "上传PDF → 多Agent自动流转分析 → 输出全套研判材料",
        "input_files": {"tender_pdf": pdf_path, "qualification_ledger": qualification_path},
        "agents": {
            "skill1_pdf_parser": parsed,
            "skill2_qualification_matcher": matched,
            "skill3_risk_reviewer": risks,
            "skill4_bid_writer": bid,
        },
        "decision": {
            "recommendation": "建议投标" if matched.get("score", 0) >= 80 and "硬性条件" not in matched.get("overall_status", "") else "谨慎投标",
            "score": matched.get("score"),
            "qualification_status": matched.get("overall_status"),
            "high_risk_count": risks.get("summary", {}).get("高风险", 0),
        },
        "exports": exports,
    }
    write_json(output_dir / "完整投标研判报告.json", report)
    report["exports"]["full_json_report"] = str(output_dir / "完整投标研判报告.json")
    return report


if __name__ == "__main__":
    demo_pdf = Path("demo_data/mock_tender.pdf")
    demo_qualification = Path("demo_data/company_qualification.xlsx")
    if not demo_pdf.exists():
        demo_pdf = Path("skills/skill1_pdf_parser/demo_tender.txt")
    if not demo_qualification.exists():
        demo_qualification = Path("skills/skill2_qualification_matcher/demo_qualification.csv")
    result = generate_report(str(demo_pdf), str(demo_qualification))
    print(f"完成：{result['exports']['full_json_report']}")
