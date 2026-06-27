# Skill3 Risk Reviewer Agent

## Goal

Review tender text and identify bid risks by severity with source evidence,
negative impact, and mitigation suggestions.

## Input

```json
{
  "parsed_document": {}
}
```

## Output

```json
{
  "agent": "risk_reviewer",
  "status": "success",
  "risks": [],
  "summary": {
    "high": 1,
    "medium": 2,
    "low": 0
  }
}
```

## Risk Levels

- `high`: may directly invalidate the bid.
- `medium`: may increase cost, delivery pressure, or contract exposure.
- `low`: can usually be clarified, negotiated, or optimized.

## Boundaries

- This Skill does not access the database.
- This Skill does not call other Agents.
- This Skill only consumes parsed tender text and evidence pages.
