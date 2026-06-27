# File Upload API

All file APIs require JWT:

```http
Authorization: Bearer <access_token>
```

## Upload Project File

```http
POST /api/v1/projects/{project_id}/files
Content-Type: multipart/form-data
```

Form fields:

| field | type | description |
| --- | --- | --- |
| file_type | string | `tender_pdf`, `qualification_excel`, or `other_material` |
| file | binary | uploaded file |

Allowed extensions:

```text
tender_pdf: .pdf, .txt
qualification_excel: .xlsx, .xls, .csv
other_material: .pdf, .doc, .docx, .xlsx, .xls, .csv, .txt
```

Response:

```json
{
  "file_type": "tender_pdf",
  "original_name": "tender.pdf",
  "stored_path": "uploads/project-id/tender_pdf_tender.pdf",
  "size": 1024,
  "content_type": "application/pdf"
}
```

## List Project Files

```http
GET /api/v1/projects/{project_id}/files
```

## Download File

```http
GET /api/v1/projects/{project_id}/files/{file_type}/download
```

## Delete File

```http
DELETE /api/v1/projects/{project_id}/files/{file_type}
```
