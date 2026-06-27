# Skill4 Proposal Writer Agent

## Goal

Generate a structured bid proposal draft from parsed tender data, qualification
matching result, and risk review result.

## Input

```json
{
  "parsed_document": {},
  "qualification_result": {},
  "risk_result": {},
  "qualification_file_path": "uploads/project/company_qualification.xlsx"
}
```

## Output

```json
{
  "agent": "proposal_writer",
  "status": "success",
  "business_outline": [],
  "technical_outline": [],
  "matched_materials": [],
  "markdown_draft": "..."
}
```

## Boundaries

- This Skill does not access the database.
- This Skill does not call other Agents.
- This Skill outputs editable draft content rather than final legal documents.
