---
name: eng-bid-respond
description: Use when a validated RFP analysis + sourced research are ready and the bid response must be written, or the user says "draft the bid", "write the tender response", "assemble the submission", or "answer the RFP". Requirement-driven from the compliance matrix, matches the RFP's mandated format exactly, compliance-first with proof-backed win-themes, every claim traceable to an RFP clause or a cited research finding, through a panel red-team gate before submission — no unsupported claim, no fabricated credential.
---

# Writing the bid response

Turn the validated analysis + sourced research into a compliant, persuasive, fully traceable
response. Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-response.md`.
Figures: the `designing-figures` skill owns them — spec before pixels, archetype from the message.

## Prerequisite
Build only from a closed analysis (`compliance_matrix.md`) and a cited research log
(`bid_research_log.md`). Draft in `01_pursuit/<ENG-ID>/3_drafting/`; freeze to `4_final/`.
Start the section map from `bid_response_outline.md.tmpl`, and each section file from
`bid_section.md.tmpl` — both in `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

## Workflow

**Content first, format last.** Write and review the content as per-section markdown; only when it
is approved do you render into the buyer's required output. Mixing the two costs both — you trim
an argument to fit a slide before knowing whether the argument is right.

```
Bid Response Progress:
- [ ] 1. Build the section map from the matrix (bid_response_outline.md) — every requirement row
        lands in exactly one section, and no section exists without a row
- [ ] 2. One MD per section in 3_drafting/sections/, from bid_section.md.tmpl — frontmatter carries
        marks, scoring basis, page budget, reqs answered, figures, evidence
- [ ] 3. Draft each section: answer in the buyer's own order; compliance first, exceptions plain;
        build its figures alongside it with the `designing-figures` skill — archetype from the
        message, never a default row of boxes. Three artefacts per figure from ONE html source:
        .html (edit here) + .png (2x, goes in the document) + .pptx (one slide, native shapes,
        so a reviewer can correct it)
- [ ] 4. Weave the 3–5 win-themes at the high-weight criteria, each backed by a cited log row or
        an indexed firm asset (A-nnn)
- [ ] 5. Traceability: every claim → [RFP §x] / A-nnn / a closed research-log row; kill any [⚠VERIFY]
- [ ] 6. REVIEW ROUNDS per section, logged in the section's own table:
        R1 panel red-team (does it score?) → R2 experienced human (what only experience sees)
        → R3 final read (cross-section consistency, format, no [⚠VERIFY] left)
- [ ] 7. ONLY NOW render — hand off to the `eng-render` skill with `--profile bid`. It gates on
        R2 status and open [⚠VERIFY], strips the internal scaffolding, and re-checks page counts
        on the rendered file. Do not assemble by hand here.
- [ ] 8. Freeze the submitted version to 4_final/ + record date; matrix fully closed
```

**Watch the `scoring` line.** A section marked **per item** needs self-contained answers per item —
six deliverables scored out of 30 each means six complete answers, and a flowing narrative that
blurs them loses marks six times over.

**Page budgets: per-question or shared?** "Max 5 A4 for 3 questions" is a shared budget; "max 3 A4
per question response" is not. Confusing them always errs toward writing too much.

**Requirement-driven, not narrative-driven.** The response is assembled from the compliance
matrix; when every row is `met` and every mandatory satisfied, it's complete. The matrix is the
fact base; the response adds the persuasion.

**Match the buyer's format exactly** — volume split, page/word limits, mandated forms. Format
non-compliance is a common auto-reject; don't impose our own structure.

## Review rounds (not one gate)
A section is finished when the rounds stop producing changes, not when it is written. Each section
carries its own log, because sections finish at different times.

- **R1 — panel red-team** (`panel-review` if installed, else a manual multi-lens pass): does it
  score? **evaluator's eye** · **legal** (exceptions clean, exposure?) · **finance**
  (priceable/deliverable at margin?) · **architect/delivery** (deliverable as staffed?).
- **R2 — experienced human.** What only experience sees: a claim that won't survive a client
  conversation, a promise delivery cannot staff, a tone wrong for this buyer.
- **R3 — final read.** Cross-section consistency, format compliance, nothing left `[⚠VERIFY]`.

**Do not collapse R1 and R2** — they fail differently. R1 is structural and can be reasoned about
from the RFT; R2 is judgement and cannot.

## Guardrails
- No unsupported claim, no fabricated credential — ever. Anything `[⚠VERIFY]` is cut or closed first.
- Every mandatory requirement is `met`; exceptions stated openly with rationale.
- Never edit a submitted volume in place — a post-submission change is a new dated version.
- **Never ship a figure as only a flat image.** Review rounds produce figure corrections; a
  reviewer who cannot edit sends the change back as prose. Every figure gets its editable
  one-slide PPTX alongside the PNG, both generated from the same HTML.
- **Look at both outputs.** Round-trip the PPTX back to an image and check the shape count — a
  one-slide export with 1-2 shapes is a screenshot in a wrapper, not an editable figure. Text that
  fits in HTML can clip as a PowerPoint shape.
