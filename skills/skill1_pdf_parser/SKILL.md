# Skill1 PDF文档解析Agent

## 目标

接收招标PDF，提取全文、表格数据与关键投标要素，并为所有结构化结论绑定原文页码。

## 输入

- `pdf_path`: 招标PDF路径，可为文字型PDF、扫描PDF或演示文本文件。

## 输出

- `pages`: 按页拆分的全文与OCR状态。
- `tables`: 表格文本化结果。
- `key_info`: 项目预算、截标时间、保证金、人员设备资质、废标条款、评分权重。
- `full_text`: 合并全文。
- `evidence`: 关键字段对应页码与原文片段。

## 可扩展点

- 已预留 `pytesseract` OCR入口。
- 若本地安装 Poppler/Tesseract，可把扫描页图片转给 OCR。
- 当前演示版严格不依赖云端服务。
