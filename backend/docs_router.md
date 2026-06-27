# Multi-Agent Router

The backend Router lives in:

```text
backend/app/agents/orchestrator.py
```

## Responsibilities

- Create `AgentContext`
- Call independent Skill Agents
- Track each Agent run status
- Normalize risk summary fields
- Build final report payload
- Emit progress updates for `Analysis`

## Workflow

```text
pdf_parser_started           10%
qualification_matcher_started 35%
risk_reviewer_started        60%
proposal_writer_started      80%
report_building              95%
completed                   100%
```

## Agent Order

```text
Skill1 PDF Parser
  -> Skill2 Qualification Matcher
  -> Skill3 Risk Reviewer
  -> Skill4 Proposal Writer
  -> Final Report
```

## Output Shape

```json
{
  "workflow": "pdf_parse -> qualification_match -> risk_review -> proposal_write -> report",
  "input_files": {},
  "agent_runs": [],
  "agents": {
    "pdf_parser": {},
    "qualification_matcher": {},
    "risk_reviewer": {},
    "proposal_writer": {}
  },
  "decision": {
    "recommendation": "bid",
    "score": 90,
    "qualification_status": "qualified",
    "high_risk_count": 0,
    "summary": "Multi-agent bidding analysis completed."
  }
}
```

## Design Rule

The Router does not contain document parsing, scoring, risk, or proposal-writing
business rules. Those remain inside independent Skill Agents.
