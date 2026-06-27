# AI招投标多智能体系统全局规则

## 系统定位

本项目用于黑客松/赛事现场路演演示，目标是在纯本地环境中完成：

上传招标PDF → Router调度四个Skill Agent → 输出投标研判报告、资质匹配Excel、风险审查PDF、投标方案文档。

## Agent协作规则

1. `router.py` 是唯一总调度入口，只负责流程编排、上下文传递和导出汇总。
2. `skills/*/main.py` 必须保持相互解耦，不允许跨Skill直接导入业务逻辑。
3. 每个Skill必须保留 `SKILL.md`、`main.py`、`test.py` 和 demo 素材，便于单独调试和扩展。
4. 所有AI式判断必须给出可追溯依据，尤其是页码、原文片段、资质台账命中项。
5. 系统必须纯本地运行，不调用云端模型或外部API。

## 依赖约束

允许依赖：

- pandas
- openpyxl
- fastapi
- pdfplumber
- pytesseract

运行服务时若本地有 `uvicorn`，`run.py` 会启动标准 FastAPI 服务；若没有，则自动进入标准库降级演示服务。

## 输出规范

- 资质匹配打分：优先导出 `.xlsx`，失败时降级为 `.csv`。
- 风险审查报告：导出 `.pdf`。
- 投标方案初稿：导出 Markdown 文档，可直接复制进 Word/WPS 继续编辑。
- 完整研判报告：导出 JSON，保留所有中间Agent结果。
