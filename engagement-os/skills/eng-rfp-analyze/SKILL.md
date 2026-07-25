---
name: eng-rfp-analyze
description: Use when an RFP / tender / ITT has arrived and needs decomposing before bidding, or the user says "analyse this RFP", "should we bid", "build the compliance matrix", "what does this tender need", or "break down the requirements". Produces a requirement/compliance matrix, an evaluation-weight score map, a multi-role analysis, evidence-backed win-themes, risk/deal-breaker flags, a materials-needed list (research vs upload), and a go/no-go — every claim cited to the RFP clause, nothing fabricated.
---

# Analysing an RFP

Decompose a tender into a scored, traceable analysis that drives a compliant, winning response.
Aligned twice — to the RFP text AND to our best practice — and read from every role's angle.
Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/rfp-analysis.md`.

## Prerequisite
The RFP pack is ingested to markdown first (`eng-ingest-source` → `01_pursuit/<ENG-ID>/1_received/_md/`)
so every requirement can be cited by clause/page. Work in `01_pursuit/<ENG-ID>/2_analysis/`, which holds four artefacts, not two:
`rfp_analysis.md` (this skill's output) · `compliance_matrix.md` (the completeness spine) ·
`clarification_log.md` (questions to the buyer + our settled readings, **query deadline is
earlier than submission**) · `bid_reuse_analysis.md` (what carries over from a prior bid — check
for one **before** drafting; most tenders are a variant of one already answered).

## Workflow

```
RFP Analysis Progress:
- [ ] 1. Extract EVERY requirement → Req ID + clause cite + mandatory/desirable flag
- [ ] 2. Build compliance_matrix.md (one row per requirement)
- [ ] 3. Map evaluation criteria + weights → where we earn points
- [ ] 4. Multi-role analysis (panel lens) — record conflicts, don't smooth
- [ ] 5. Derive 3–5 evidence-backed win-themes (no proof → not a theme)
- [ ] 6. Flag risks / red-flags / deal-breakers (+ clarification questions)
- [ ] 7. Materials-needed list: WE research vs YOU upload (be specific)
- [ ] 8. Go / no-go recommendation with conditions
```

Fill `rfp_analysis.md` (steps 3–8) and `compliance_matrix.md` (step 2) from the templates in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

**Step 1 — completeness.** Read the whole RFP and every appendix/schedule. Extract *all*
obligations (scope, qualifications, submission mechanics, format rules, deadlines, weights,
contract terms), not just the obvious ones. Cite each: `[RFP §x]`.

**Step 4 — multi-role.** Reuse the Panel Framework roles if installed (evaluator's-eye, solution
architect, engagement partner/commercial, legal, delivery lead, sector SME); else walk the lenses
manually. Each surfaces what a single reader misses.

**Step 7 — materials-needed.** Be specific ("the 2024 utility DWH case study with the €X saving",
not "a relevant case study"). This list is the input to `eng-bid-research` and the user's upload ask.

## Guardrails (the doctrine)
- **Nothing fabricated.** A capability/credential/metric we can't source becomes a materials-needed
  item or `[⚠VERIFY]` — never an asserted claim.
- **Dual alignment.** Every response approach maps to a requirement AND to our methodology.
- **Traceable both ways.** Requirement → our response; any claim → its requirement + evidence.

## Hand-off
Gaps + the materials-needed list → `eng-bid-research`. On a go, the matrix + win-themes → `eng-bid-respond`.
