"""Qualification matching Skill."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


REQUIRED_ITEMS = [
    {"name": "营业执照", "type": "证书", "hard": True, "keywords": ["营业执照"]},
    {"name": "投标保证金凭证", "type": "材料", "hard": True, "keywords": ["保证金", "缴纳凭证"]},
    {"name": "项目经理证书", "type": "人员", "hard": True, "keywords": ["PMP", "信息系统项目管理师"]},
    {"name": "近三年类似业绩2项", "type": "业绩", "hard": False, "keywords": ["智慧园区", "运维", "类似项目"]},
    {"name": "团队不少于8人", "type": "人员", "hard": False, "keywords": ["团队", "8"]},
]


def _load_qualifications(path: str) -> List[Dict[str, Any]]:
    """Load enterprise qualification ledger from Excel or CSV."""

    qpath = Path(path)
    if qpath.suffix.lower() in {".xlsx", ".xls"}:
        import pandas as pd

        return pd.read_excel(qpath).fillna("").to_dict("records")
    if qpath.suffix.lower() == ".csv":
        import pandas as pd

        return pd.read_csv(qpath).fillna("").to_dict("records")
    return []


def _row_text(rows: List[Dict[str, Any]]) -> str:
    return "\n".join(" ".join(str(value) for value in row.values()) for row in rows)


def run(parsed_data: Dict[str, Any], qualification_path: str) -> Dict[str, Any]:
    """Run qualification matching and score calculation."""

    rows = _load_qualifications(qualification_path)
    ledger_text = _row_text(rows)
    checks: List[Dict[str, Any]] = []
    missing_materials: List[str] = []
    hard_fail = False

    for item in REQUIRED_ITEMS:
        matched = any(keyword in ledger_text for keyword in item["keywords"])
        if not matched:
            missing_materials.append(item["name"])
            if item["hard"]:
                hard_fail = True
        checks.append(
            {
                "requirement": item["name"],
                "type": item["type"],
                "hard": item["hard"],
                "status": "完全达标" if matched else ("硬性条件不满足" if item["hard"] else "材料缺失"),
                "evidence": "企业资质台账命中关键词" if matched else "资质台账未检索到对应材料",
            }
        )

    matched_count = sum(1 for check in checks if check["status"] == "完全达标")
    score = round(matched_count / len(checks) * 100)
    if hard_fail:
        overall_status = "硬性条件不满足（存在废标风险）"
        score = min(score, 59)
    elif missing_materials:
        overall_status = "材料缺失"
    else:
        overall_status = "完全达标"

    bonus_tips = []
    scoring = parsed_data.get("key_info", {}).get("评分权重", "")
    if "技术" in scoring:
        bonus_tips.append("技术标权重较高，建议补充运维SLA、应急响应、质量保障和项目团队履历。")
    if "商务" in scoring:
        bonus_tips.append("商务标可强化同类项目合同、验收报告和客户评价材料。")
    if score < 90:
        bonus_tips.append("优先补齐硬性材料，再准备可量化业绩证明以提升评分稳定性。")

    return {
        "agent": "Skill2 资质匹配打分Agent",
        "status": "success",
        "qualification_file": qualification_path,
        "score": score,
        "overall_status": overall_status,
        "checks": checks,
        "missing_materials": missing_materials,
        "bonus_tips": bonus_tips,
        "ledger_rows": len(rows),
    }
