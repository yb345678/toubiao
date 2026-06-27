"""Bid proposal drafting Skill."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _load_material_summary(path: str) -> List[str]:
    """Read enterprise material names from Excel/CSV."""

    qpath = Path(path)
    if not qpath.exists():
        return []
    import pandas as pd

    if qpath.suffix.lower() in {".xlsx", ".xls"}:
        rows = pd.read_excel(qpath).fillna("").to_dict("records")
    else:
        rows = pd.read_csv(qpath).fillna("").to_dict("records")
    summary = []
    for row in rows[:12]:
        name = row.get("名称") or row.get("name") or next(iter(row.values()), "")
        desc = row.get("描述") or row.get("description") or ""
        summary.append(f"{name}：{desc}")
    return summary


def run(parsed_data: Dict[str, Any], match_result: Dict[str, Any], qualification_path: str) -> Dict[str, Any]:
    """Generate editable Markdown bid proposal draft."""

    key_info = parsed_data.get("key_info", {})
    materials = _load_material_summary(qualification_path)
    score = match_result.get("score", 0)
    missing = match_result.get("missing_materials", [])
    project_name = "智慧园区运维服务采购项目"

    outline = {
        "商务标": [
            "投标函与法定代表人授权书",
            "企业基本情况与营业执照",
            "近三年类似项目业绩",
            "项目团队资质与证书",
            "投标保证金缴纳凭证",
            "商务偏离表与服务承诺",
        ],
        "技术标": [
            "项目理解与总体服务目标",
            "运维服务组织架构",
            "7x24响应与应急处置机制",
            "质量保障、SLA与验收方法",
            "安全管理与数据保密措施",
            "实施计划、交付里程碑与风险控制",
        ],
    }

    material_block = "\n".join(f"- {item}" for item in materials) or "- 暂无可匹配素材，请补充企业资质库。"
    missing_block = "\n".join(f"- {item}" for item in missing) or "- 当前未发现缺失材料。"
    draft = f"""
## 一、投标项目概况

- 项目名称：{project_name}
- 项目预算：{key_info.get("项目预算", "未识别")}
- 截标时间：{key_info.get("截标时间", "未识别")}
- 投标保证金：{key_info.get("保证金", "未识别")}
- 评分细则：{key_info.get("评分权重", "未识别")}

## 二、商务标应答

本公司具备本项目所需基础资质，资质匹配得分为 **{score}分**。商务标建议围绕营业执照、项目经理证书、保证金凭证、同类项目业绩和团队人员清单展开。

### 已匹配企业素材

{material_block}

### 待补充材料

{missing_block}

## 三、技术标应答

针对招标文件技术评分权重，建议以“稳定运维、快速响应、可量化SLA、风险闭环”为主线组织技术标。

1. 项目理解：说明智慧园区业务连续性、设备联动、用户服务体验等核心目标。
2. 服务组织：设置项目经理、驻场工程师、二线专家和客户成功接口人。
3. 响应机制：建立7x24值守、15分钟响应、重大故障升级和复盘机制。
4. 质量保障：通过巡检计划、问题台账、月度报告和验收指标证明可控交付。
5. 风险控制：对人员变更、系统故障、数据安全和供应商协同提出预案。

## 四、投标结论

建议投标。若存在硬性条件不满足，应在正式投标前完成材料补齐并再次运行本系统复核。
""".strip()

    return {
        "agent": "Skill4 投标方案生成Agent",
        "status": "success",
        "outline": outline,
        "matched_materials": materials,
        "markdown_draft": draft,
    }
