# API接口文档

## 服务地址

本地默认地址：

```text
http://127.0.0.1:8000
```

## 1. 健康检查

```http
GET /health
```

响应：

```json
{
  "status": "ok",
  "service": "ai-bidding-agent-system"
}
```

## 2. 内置Demo分析

```http
GET /api/demo
```

用途：不上传文件，直接使用 `demo_data/mock_tender.pdf` 和 `demo_data/company_qualification.xlsx` 跑完整业务闭环。

响应：完整投标研判报告 JSON。

## 3. 上传文件分析

```http
POST /api/analyze
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `tender_pdf` | file | 招标PDF，也支持演示txt/pdf文本素材 |
| `qualification_file` | file | 企业资质库，支持 `.xlsx`、`.xls`、`.csv` |

响应：完整投标研判报告 JSON，包含：

- `agents.skill1_pdf_parser`
- `agents.skill2_qualification_matcher`
- `agents.skill3_risk_reviewer`
- `agents.skill4_bid_writer`
- `decision`
- `exports`

## 4. 下载导出文件

```http
GET /download?path=outputs/xxx/资质匹配打分.xlsx
```

安全限制：只能下载 `outputs` 目录下由系统生成的文件。

## curl示例

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/demo
curl -X POST http://127.0.0.1:8000/api/analyze \
  -F "tender_pdf=@demo_data/mock_tender.pdf" \
  -F "qualification_file=@demo_data/company_qualification.xlsx"
```
