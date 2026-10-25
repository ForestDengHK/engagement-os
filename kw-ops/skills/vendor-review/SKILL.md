---
name: vendor-review
description: Use when a vendor or product needs evaluating — reviewing a new vendor proposal, deciding whether to renew or replace a contract, comparing two vendors or platforms side by side, or building a TCO breakdown and negotiation points before a procurement or architecture decision.
argument-hint: "<vendor name or proposal>"
---

# /vendor-review

Evaluate a vendor with structured analysis covering cost, risk, performance, and fit, ending in a
recommendation.

## Usage

```
/vendor-review $ARGUMENTS
```

## What I Need From You

- **Vendor name**: Who are you evaluating?
- **Context**: New vendor evaluation, renewal decision, or comparison?
- **Details**: Contract terms, pricing, proposal document, or current performance data

## Evaluation Framework

### Cost Analysis (Total Cost of Ownership)
- Total cost of ownership (not just license fees)
- Implementation and migration costs
- Training and onboarding costs
- Ongoing support and maintenance
- Exit costs (data migration, contract termination)

### Risk Assessment
- Vendor financial stability
- Security and compliance posture
- Concentration risk (single vendor dependency)
- Contract lock-in and exit terms
- Business continuity and disaster recovery

### Performance Metrics
- SLA compliance
- Support response times
- Uptime and reliability
- Feature delivery cadence
- Customer satisfaction

### Comparison Matrix
When comparing vendors, produce a side-by-side matrix covering: pricing, features, integrations, security, support, contract terms, and references.

## Where it goes in an engagement repo

An engagement-os repo has `_pm/raid_and_decisions.md` and `.claude/project-context.md`. In one:

- **Write the review** as `<snake_case_vendor>_vendor_review.md` in the folder of the work it feeds: the target-architecture or cost-model deliverable folder (e.g. `02_delivery/3_target_architecture/`, `02_delivery/5_cost_model/`), `00_research/1_analysis/` in a research assignment, or `01_pursuit/<ENG-ID>/2_analysis/` when assessing a partner or subcontractor for a bid.
- **The cost model stays the single source of the numbers.** If the engagement has one, link to it rather than copying figures that will drift.
- **Cite every figure and claim**: from a vendor proposal or price list `[T3:REF <document> <page>]`; our own research or public pricing `[T3:OWN <source>, <YYYY-MM-DD>]`; client volumes or usage measured from the system `[T1:SYS §x]`. A vendor's claim is reference-tier — corroborate it or flag it `[⚠VERIFY vs <source>]`; a recommendation never rests on an open `[⚠VERIFY]` figure.
- **Risks** found go to the Risks table in `_pm/raid_and_decisions.md` with the next free `R<n>` (see `risk-assessment`); once the client chooses, record a Decision Log row (`DEC-<n>`).
- **Contract terms** → `review-contract` (kw-legal), stating that the client is the buyer — the kw-legal playbook's supplier-side positions don't apply.
- **Disclose relationships.** If the firm has an alliance or commercial relationship with a vendor under review, say so in the review and follow the firm's independence policy.

Outside an engagement repo, give the review in the reply and ask where to save it.

## Output

Amounts in the client's currency (default €), excluding VAT, with the pricing date.

```markdown
## Vendor Review: [Vendor Name]
**Date:** [YYYY-MM-DD] | **Type:** [New / Renewal / Comparison] | **Sources:** [documents reviewed]

### Summary
[2-3 sentence recommendation]

### Cost Analysis
| Component | Annual Cost | Notes |
|-----------|-------------|-------|
| License/subscription | €[X] | [Per seat, flat, usage-based — cited] |
| Implementation | €[X] | [One-time] |
| Support/maintenance | €[X] | [Included or add-on] |
| **Total Year 1** | **€[X]** | |
| **Total 3-Year** | **€[X]** | |

### Risk Assessment
| RAID ID | Risk | Likelihood | Impact | Mitigation |
|---------|------|-----------|--------|------------|
| R<n> | [Risk] | High/Med/Low | High/Med/Low | [Mitigation] |

### Strengths
- [Strength 1]
- [Strength 2]

### Concerns
- [Concern 1]
- [Concern 2]

### Recommendation
[Proceed / Negotiate / Pass] — [Reasoning]

### Negotiation Points
- [Leverage point 1]
- [Leverage point 2]
```

## If Tools Are Connected

- **Knowledge base** (e.g. SharePoint, Confluence): search for existing vendor evaluations, contracts and performance reviews, and procurement policies and approval thresholds.
- **Procurement system**: pull current contract terms, spend history and renewal dates; compare pricing against existing agreements.

## Tips

1. **Upload the proposal** — I can extract pricing, terms, and SLAs from vendor documents.
2. **Compare vendors** — "Compare Vendor A vs Vendor B" gets you a side-by-side analysis.
3. **Include current spend** — For renewals, knowing what you pay now helps evaluate price changes.
