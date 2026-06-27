# Skill2 资质匹配打分Agent

## 目标

接收PDF解析结构化数据与企业资质Excel库，逐条校验投标门槛并输出0-100匹配得分。

## 输入

- `parsed_data`: Skill1输出。
- `qualification_path`: 企业资质Excel或CSV路径。

## 输出

- `score`: 0-100综合匹配分。
- `status`: 完全达标、材料缺失、硬性条件不满足。
- `checks`: 逐条门槛校验结果。
- `missing_materials`: 缺失材料清单。
- `bonus_tips`: 可提升加分项提示。
