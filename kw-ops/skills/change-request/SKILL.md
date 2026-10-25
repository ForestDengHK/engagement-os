---
name: change-request
description: Use when a scope, system or process change needs a change request before it is approved — preparing a change record for client sign-off or CAB review, documenting risk and rollback steps before a deployment or cut-over, or planning stakeholder communications for a rollout. Not for a reviewer's edit to an engagement artefact that must flow downstream (eng-propagate-change).
argument-hint: "<change description>"
---

# /change-request

Create a structured change request with impact analysis, risk assessment, and rollback plan, and
record it in the engagement repo's own registers.

## Usage

```
/change-request $ARGUMENTS
```

## Hand off first

| The ask is really… | Use instead |
|---|---|
| "I edited this file — what does it affect?" (an artefact change, not a client change) | `eng-propagate-change` |
| Sizing or pricing the change (days, cost, price) | `eng-estimate` — its method serves a delivery-side change request; this skill links to its output |
| The engagement itself grew a phase (bid won, study became delivery) | `/eng-upgrade` |
| A project fact moved (scope, stack, stakeholder) | `eng-maintain-memory` for `.claude/project-context.md` |

## Where it goes in an engagement repo

An engagement-os repo has `_pm/raid_and_decisions.md` and `.claude/project-context.md`. In one:

1. **Find the existing change log.** Search `_pm/` for a change register (a file or a section whose name contains "change", or a client-mandated CR register). If one exists, add the CR there in **its** ID scheme and columns.
2. **If none exists, don't create a parallel file.** Add a `## Change Requests` section to `_pm/raid_and_decisions.md`, after the Decision Log: `| ID | Date | Change | Requested by | Impact | Status | Decision |`, with IDs `CR-1`, `CR-2`, … Status: `draft` · `pending approval` · `approved` · `rejected` · `in progress` · `complete`.
3. **Write the full request** (the Output template below) to `_pm/CR-<n>_<snake_case_title>.md` and link it from the register row.
4. **Feed the RAID tables in place.** Each risk in the CR becomes a row in the Risks table with the next free `R<n>` (scored as in `risk-assessment`); new assumptions → `A<n>`; dependencies → `D<n>`. Reference the CR ID in each row.
5. **On approval**, add a Decision Log row (`DEC-<n>`: decision, rationale, made by) and set the CR's status and `Decision` cell to that ID.
6. **Log it.** Add a dated entry at the top of `_pm/engagement_log.md`, following the entry template in that file.

Cite every fact in the engagement's style: `[T1:SYS §x]` measured from the system,
`[T2:WS <session> <date>]` from a workshop, `[T3:REF <source> <loc>]` from a document, `[T3:OWN <source>]`
our own research, `[RFP §x]` from the tender. Anything not yet supported gets `[⚠VERIFY vs <source>]`.
Before a CR goes to the client, run `eng-check`; render it with `eng-render` if it must leave as Word/PDF.

Outside an engagement repo, give the CR in the reply and ask where to save it.

## Change Management Framework

Apply the assess-plan-execute-sustain framework when building the request:

### 1. Assess
- What is changing?
- Who is affected?
- How significant is the change? (Low / Medium / High)
- What resistance should we expect?

### 2. Plan
- Communication plan (who, what, when, how)
- Training plan (what skills are needed, how to deliver)
- Support plan (help desk, champions, FAQs)
- Timeline with milestones

### 3. Execute
- Announce and explain the "why"
- Train and support
- Monitor adoption
- Address resistance

### 4. Sustain
- Measure adoption and effectiveness
- Reinforce new behaviors
- Address lingering issues
- Document lessons learned

## Communication Principles

- Explain the **why** before the **what**
- Communicate early and often
- Use multiple channels
- Acknowledge what's being lost, not just what's being gained
- Provide a clear path for questions and concerns

## Output

```markdown
## Change Request CR-<n>: [Title]
**Requester:** [Name] | **Date:** [YYYY-MM-DD] | **Priority:** [Critical/High/Medium/Low]
**Status:** Draft | Pending Approval | Approved | In Progress | Complete
**Register:** [link to the register row] | **Estimate:** [link to the eng-estimate output, if sized]

### Description
[What is changing and why — cited]

### Business Justification
[Why this change is needed — cost savings, compliance, efficiency, risk reduction]

### Impact Analysis
| Area | Impact | Details |
|------|--------|---------|
| Users | [High/Med/Low/None] | [Who is affected and how] |
| Systems | [High/Med/Low/None] | [What systems are affected] |
| Processes | [High/Med/Low/None] | [What workflows change] |
| Cost | [High/Med/Low/None] | [Budget impact] |
| Scope / deliverables | [High/Med/Low/None] | [Which SOW items or D-numbers change] |

### Risk Assessment
| RAID ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|------------|
| R<n> | [Risk] | [H/M/L] | [H/M/L] | [How to mitigate] |

### Implementation Plan
| Step | Owner | Timeline | Dependencies |
|------|-------|----------|--------------|
| [Step] | [Person] | [Date] | [What it depends on — D<n>] |

### Communication Plan
| Audience | Message | Channel | Timing |
|----------|---------|---------|--------|
| [Who] | [What to tell them] | [How] | [When] |

### Rollback Plan
[Step-by-step plan to reverse the change if needed]
- Trigger: [When to roll back]
- Steps: [How to roll back]
- Verification: [How to confirm rollback worked]

### Approvals Required
| Approver | Role | Status |
|----------|------|--------|
| [Name] | [Role] | Pending |
```

## If Tools Are Connected

- **ITSM tool** (e.g. ServiceNow): create the change ticket and pull the CAB schedule and approval workflow; record the ticket number in the register row.
- **Project tracker** (e.g. Azure DevOps, Jira): link implementation tasks and dependencies.
- **Chat or email**: draft stakeholder notifications for the communication plan — never send without the user's go-ahead.

## Tips

1. **Be specific about impact** — "Everyone" is not an impact assessment. "200 users in the billing team" is.
2. **Always have a rollback plan** — Even if you're confident, plan for failure.
3. **Communicate early** — Surprises create resistance. Previews create buy-in.
