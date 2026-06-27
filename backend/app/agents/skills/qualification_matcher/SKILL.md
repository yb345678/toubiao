# Skill2 Qualification Matching Agent

## Goal

Match parsed tender requirements against an enterprise qualification ledger and
produce a 0-100 score, hard-failure signals, missing materials, and bonus tips.

## Input

```json
{
  "parsed_document": {},
  "qualification_file_path": "uploads/project/company_qualification.xlsx"
}
```

## Output

```json
{
  "agent": "qualification_matcher",
  "status": "success",
  "score": 90,
  "overall_status": "qualified",
  "checks": [],
  "missing_materials": [],
  "bonus_tips": []
}
```

## Boundaries

- This Skill does not access the database.
- This Skill does not call other Agents.
- This Skill accepts parsed tender data and a file path only.
