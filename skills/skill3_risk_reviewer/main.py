"""Tender risk review Skill."""

from __future__ import annotations

from typing import Any, Dict, List

from utils import find_evidence


RISK_RULES = [
    {
        "level": "高风险",
        "keywords": ["废标", "无效投标", "否决投标"],
        "impact": "触发后可能直接导致投标文件被否决。",
        "mitigation": "建立硬性材料清单，投标前由商务、法务、项目经理三方复核盖章版材料。",
    },
    {
        "level": "中风险",
        "keywords": ["驻场", "7x24", "响应时间", "赔偿", "违约金"],
        "impact": "可能显著抬高交付成本或产生履约处罚。",
        "mitigation": "测算驻场与响应成本，在技术方案中明确服务边界、升级机制和例外条款。",
    },
    {
        "level": "低风险",
        "keywords": ["可协商", "建议", "优先"],
        "impact": "对中标结果影响较低，但可能影响后续合同谈判空间。",
        "mitigation": "在偏离表或澄清问题中温和说明企业建议方案。",
    },
]


def run(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run risk recognition against full tender text."""

    pages = parsed_data.get("pages", [])
    risks: List[Dict[str, Any]] = []
    for rule in RISK_RULES:
        evidence = find_evidence(pages, rule["keywords"], limit=10)
        for item in evidence:
            risks.append(
                {
                    "level": rule["level"],
                    "source_page": item["page"],
                    "original_text": item["quote"],
                    "negative_impact": rule["impact"],
                    "mitigation": rule["mitigation"],
                }
            )

    if not risks:
        risks.append(
            {
                "level": "低风险",
                "source_page": 1,
                "original_text": "未命中高频风险词，仍需人工复核合同专用条款。",
                "negative_impact": "遗漏非标准条款可能影响最终报价或履约承诺。",
                "mitigation": "答辩演示中建议保留法务复核节点，形成AI+人工闭环。",
            }
        )

    summary = {
        "高风险": sum(1 for risk in risks if risk["level"] == "高风险"),
        "中风险": sum(1 for risk in risks if risk["level"] == "中风险"),
        "低风险": sum(1 for risk in risks if risk["level"] == "低风险"),
    }
    return {"agent": "Skill3 投标风险审查Agent", "status": "success", "risks": risks, "summary": summary}
