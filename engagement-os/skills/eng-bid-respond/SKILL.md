---
name: eng-bid-respond
description: Use when a validated RFP analysis + sourced research are ready and the bid response must be written, or the user says "draft the bid", "write the tender response", "assemble the submission", or "answer the RFP". Requirement-driven from the compliance matrix, matches the RFP's mandated format exactly, compliance-first with proof-backed win-themes, every claim traceable to an RFP clause or a cited research finding, through a panel red-team gate before submission — no unsupported claim, no fabricated credential.
---

# Writing the bid response

Turn the validated analysis + sourced research into a compliant, persuasive, fully traceable
response. Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-response.md`.

## Prerequisite
Build only from a closed analysis (`compliance_matrix.md`) and a cited research log
(`bid_research_log.md`). Draft in `01_pursuit/<ENG-ID>/3_drafting/`; freeze to `4_final/`.
Start the section map from `bid_response_outline.md.tmpl` in `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

## Workflow

```
Bid Response Progress:
- [ ] 1. Match the RFP's mandated format/volumes/limits/forms EXACTLY (build the section map)
- [ ] 2. Assemble FROM the matrix — every requirement row → a response section (not free-written)
- [ ] 3. Compliance first: every mandatory fully met; state exceptions plainly, never bury them
- [ ] 4. Weave the 3–5 win-themes, each backed by a cited research-log item, at high-weight criteria
- [ ] 5. Traceability: every claim → [RFP §x] or a closed research-log row; kill any [⚠VERIFY]
- [ ] 6. Panel red-team gate (or manual multi-lens) → clear red-lines
- [ ] 7. Freeze the submitted version to 4_final/ + record date; matrix fully closed
```

**Requirement-driven, not narrative-driven.** The response is assembled from the compliance
matrix; when every row is `met` and every mandatory satisfied, it's complete. The matrix is the
fact base; the response adds the persuasion.

**Match the buyer's format exactly** — volume split, page/word limits, mandated forms. Format
non-compliance is a common auto-reject; don't impose our own structure.

## The red-team gate (not optional)
Before submission, red-team with the Panel Framework (`panel-review`) if installed, else a manual
multi-lens pass: **evaluator's eye** (does it score?), **legal** (exceptions clean, exposure?),
**finance** (priceable/deliverable at margin?), **architect/delivery** (deliverable as staffed?).
Fix red-lines before calling it submission-ready.

## Guardrails
- No unsupported claim, no fabricated credential — ever. Anything `[⚠VERIFY]` is cut or closed first.
- Every mandatory requirement is `met`; exceptions stated openly with rationale.
- Never edit a submitted volume in place — a post-submission change is a new dated version.
