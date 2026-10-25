---
name: process-doc
description: Use when a business process needs documenting — formalising a process that lives in someone's head, building a RACI to clarify who owns what, writing an SOP for a handover or audit, or capturing the exceptions and edge cases of how work actually gets done, as-is or to-be.
argument-hint: "<process name or description>"
---

# /process-doc

Document a business process as a complete standard operating procedure (SOP): RACI, flowchart and
detailed steps.

## Usage

```
/process-doc $ARGUMENTS
```

## How It Works

Walk me through the process — describe it, paste existing docs, or just tell me the name and I'll ask the right questions. I'll produce a complete SOP.

Before drafting, search the repo (and any connected knowledge base) for an existing document on
this process, and update it rather than writing a duplicate.

## Where it goes in an engagement repo

An engagement-os repo has `_pm/raid_and_decisions.md` and `.claude/project-context.md`. Pick the
location by what the document is:

| The document is… | Write it to |
|---|---|
| The client's process **as it runs today** (discovery evidence) | `02_delivery/1_discovery/4_output/<snake_case_process>_process.md`. If it shows a current-state problem, write that up as a finding with `eng-write-findings`, citing this file — a finding is the fact baseline, not this SOP |
| A **to-be** process, SOP or handover for the client | The deliverable folder it belongs to (e.g. `02_delivery/3_target_architecture/`, or the handover deliverable's folder) as `<snake_case_process>_sop.md`; if it is a deliverable in its own right, register it in `DELIVERABLES.md` via `eng-maintain-memory` |
| Part of a standalone research assignment | `00_research/1_analysis/<snake_case_process>.md` |
| Our own engagement process (how the team works) | `_pm/<snake_case_process>.md` |

- **Names in the RACI** come from the stakeholder map in `.claude/project-context.md`; a person or role not in it is a project fact — record it with `eng-maintain-memory`, don't invent one.
- **Cite each step** in the engagement's style: `[T2:WS <session> <date>]` for what the room said, `[T3:REF <source> <loc>]` for a client document, `[T1:SYS §x]` for what a system log or config shows. Where a step rests on one person's account or conflicts with a document, flag `[⚠VERIFY vs <source>]`.
- **Open questions** (unknown owner, undocumented exception) go to `02_delivery/0_mobilisation/discovery_questions.md` if the repo has one.
- **Risks** the process exposes go to the Risks table in `_pm/raid_and_decisions.md` with the next free `R<n>` (see `risk-assessment`).

Outside an engagement repo, give the SOP in the reply and ask where to save it.

## Output

```markdown
## Process Document: [Process Name]
**Owner:** [Person/Team] | **Last Updated:** [YYYY-MM-DD] | **Review Cadence:** [Quarterly/Annually]
**State:** [As-is / To-be] | **Sources:** [held-notes / documents this is based on]

### Purpose
[Why this process exists and what it accomplishes]

### Scope
[What's included and excluded]

### RACI Matrix
| Step | Responsible | Accountable | Consulted | Informed |
|------|------------|-------------|-----------|----------|
| [Step] | [Who does it] | [Who owns it] | [Who to ask] | [Who to tell] |

### Process Flow
[ASCII flowchart or step-by-step description. For a client-grade diagram, hand the steps to designing-figures.]

### Detailed Steps

#### Step 1: [Name]
- **Who**: [Role]
- **When**: [Trigger or timing]
- **How**: [Detailed instructions]
- **Output**: [What this step produces]
- **Source**: [citation]

#### Step 2: [Name]
[Same format]

### Exceptions and Edge Cases
| Scenario | What to Do |
|----------|-----------|
| [Exception] | [How to handle it] |

### Metrics
| Metric | Target | How to Measure |
|--------|--------|----------------|
| [Metric] | [Target] | [Method] |

### Related Documents
- [Repo path of related process, policy, finding or deliverable]
```

## If Tools Are Connected

- **Knowledge base** (e.g. SharePoint, Confluence): search for existing process documentation to update rather than duplicate; publish only when the user asks.
- **Project tracker** (e.g. Azure DevOps, Jira): link the process to related work items and create tasks for improvement actions.

## Tips

1. **Start messy** — You don't need a perfect description. Tell me how it works today and I'll structure it.
2. **Include the exceptions** — "Usually we do X, but sometimes Y" is the most valuable part to document.
3. **Name the people** — Even if roles change, knowing who does what today helps get the process right.
