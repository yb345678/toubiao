# Skill4 投标方案生成Agent

## 目标

依据资质匹配分数、评分细则和企业资质素材，生成商务标、技术标写作大纲与可编辑Markdown投标初稿。

## 输入

- `parsed_data`: Skill1输出。
- `match_result`: Skill2输出。
- `qualification_path`: 企业资质库。

## 输出

- `outline`: 商务标与技术标大纲。
- `markdown_draft`: 可直接编辑的投标初稿。
- `matched_materials`: 已匹配素材摘要。
