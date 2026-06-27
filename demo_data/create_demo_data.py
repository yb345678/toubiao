"""Generate local demo tender and qualification ledger."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent


TENDER_TEXT = """--- PAGE 1 ---
项目名称：智慧园区运维服务采购项目
采购单位：某高新区产业发展中心
项目预算：380万元
最高限价：380万元
截标时间：2026年07月18日 09:30
投标保证金：5万元
评分权重：商务30分，技术45分，价格25分。

--- PAGE 2 ---
人员设备资质：项目经理须具备PMP或信息系统项目管理师证书，团队不少于8人，需提供近三年类似项目业绩2项。
技术要求：中标人须提供7x24小时响应，重大故障30分钟内到场或远程处理，按月提交运维报告。
废标条款：未提供有效营业执照、投标保证金缴纳凭证、项目经理证书或法定代表人授权书的，按无效投标处理。

--- PAGE 3 ---
商务评分：企业同类项目业绩每项5分，最高15分；项目团队证书最高10分；服务承诺最高5分。
技术评分：项目理解10分，服务方案15分，应急响应10分，质量保障10分。
合同风险：如未达到响应时间，采购人可按次扣减服务费；严重违约可解除合同。
"""


def main() -> None:
    ROOT.mkdir(exist_ok=True)
    (ROOT / "mock_tender.pdf").write_text(TENDER_TEXT, encoding="utf-8")

    rows = [
        {"类别": "证书", "名称": "营业执照", "描述": "统一社会信用代码有效，经营范围包含软件开发与运维服务", "有效期": "2035-12-31"},
        {"类别": "材料", "名称": "投标保证金缴纳凭证", "描述": "财务部可在投标前开具银行转账凭证", "有效期": "2026-12-31"},
        {"类别": "人员", "名称": "项目经理PMP证书", "描述": "张三，PMP证书编号PMP-2025-001，负责大型运维项目", "有效期": "2028-05-20"},
        {"类别": "业绩", "名称": "智慧园区运维项目A", "描述": "2024年智慧园区驻场运维合同及验收报告", "有效期": "长期"},
        {"类别": "业绩", "名称": "政务云平台运维项目B", "描述": "2025年政务云平台运维与应急响应服务", "有效期": "长期"},
        {"类别": "人员", "名称": "团队8人清单", "描述": "项目经理1人，技术专家2人，运维工程师5人", "有效期": "2026-12-31"},
    ]
    try:
        import pandas as pd

        pd.DataFrame(rows).to_excel(ROOT / "company_qualification.xlsx", index=False)
    except Exception:
        import csv

        with (ROOT / "company_qualification.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()
