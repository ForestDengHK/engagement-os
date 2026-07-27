---
name: eng-bid-respond
description: Use when a validated RFP analysis + sourced research are ready and the bid response must be written, or the user says "draft the bid", "write the tender response", or "answer the RFP". Requirement-driven from the compliance matrix, matches the RFP's mandated format exactly, compliance-first with proof-backed win-themes, every claim traceable to an RFP clause or a cited research finding, through a panel red-team gate before submission — no unsupported claim, no fabricated credential. (Turning the finished sections into the submission FILE is eng-render.)
---

# Writing the bid response

Turn the validated analysis + sourced research into a compliant, persuasive, fully traceable
response. Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-response.md`.
Figures: the `designing-figures` skill owns them — spec before pixels, archetype from the message.

## Prerequisite
Build from a **settled** analysis and a cited research log (`bid_research_log.md`). Settled means
the go/no-go decision is taken, every requirement is extracted into `compliance_matrix.md`, and the
evidence is indexed — **not** that the rows are `met`. Rows close *because* the response answers
them; waiting for a closed matrix would mean never starting. Draft in
`01_pursuit/<ENG-ID>/3_drafting/`; freeze to `4_final/`. Start the section map from
`bid_response_outline.md.tmpl`, and each section file from `bid_section.md.tmpl` — both in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

**If missing:** no matrix or no go decision → `Skill(engagement-os:eng-rfp-analyze)`; no research
log → `Skill(engagement-os:eng-bid-research)`. Drafting before the go decision writes chapters it
may throw away, and a claim with no cited row cannot survive the traceability gate — lint errors on
a `BR-nnn` no log knows and warns on a section resting on an `open` row.

Before writing or reviewing, invoke `Skill(engagement-os:eng-propagate-change)`. Work only the
sections it identifies. A reviewed section whose content or load-bearing dependency changed is no
longer reviewed even if its frontmatter still says so; the change-impact gate returns it to the
revise state of the round it had reached.

## Workflow

**Content first, format last.** Write and review the content as per-section markdown; only when it
is approved do you render into the buyer's required output. Mixing the two costs both — you trim
an argument to fit a slide before knowing whether the argument is right.

```
Bid Response Progress:
- [ ] 1. Build the section map from the matrix (bid_response_outline.md) — every requirement row
        lands in a written section OR under a named control (a submission control sheet, the
        clarification register, commercial sign-off, contract acceptance). Process obligations and
        accepted terms are not prose questions; inventing a section for them makes the matrix lie.
        A requirement the RFT scores in two places names its primary section and its second one.
        Lint errors if a row appears nowhere at all
- [ ] 2. One MD per section, **one directory per volume** — `3_drafting/sections/v1/`, `v2/`, `v3/`
        — from bid_section.md.tmpl; frontmatter carries marks, scoring basis, page budget, reqs
        answered, figures, evidence. Each volume renders into its own file, which is how the
        buyer's mandated volume split survives into the artefact, and it is what makes a volume
        nobody has started visible. A figure reference from a volume directory is
        `../../figures/F-nn_x.png`. **Draft every volume, not only the scored one:** the pass/fail
        questionnaires (H&S, data protection, information security) are prose answers that must
        exist before the evidence arrives, and lint errors on an outline row marked drafted with
        no file behind it
- [ ] 3. Draft each section: answer in the buyer's own order; compliance first, exceptions plain;
        build its figures alongside it with the `designing-figures` skill — archetype from the
        message, never a default row of boxes. Three artefacts per figure from ONE html source:
        .html (edit here) + .png (2x, goes in the document) + .pptx (one slide, native shapes,
        so a reviewer can correct it). A figure bound for an A4 *document* keeps the skill's
        canvas and grid but drops slide furniture that the document already provides — the
        section heading and the markdown caption. The editable-master pointer goes on the
        `**Figure source.**` line, never in the caption: the strip removes that line, and a
        caption naming `F-01_x.html` ships our internal filenames to the evaluator
- [ ] 4. Weave the 3–5 win-themes at the high-weight criteria, each backed by a cited log row or
        an indexed firm asset (A-nnn)
- [ ] 5. Traceability: every claim → [RFP §x] / A-nnn / a `closed` research-log row (`BR-nnn`);
        kill any [⚠VERIFY]. Lint reports a section resting on an `open` row and counts every
        unresolved marker while you draft — not for the first time at the freeze
- [ ] 6. REVIEW ROUNDS per section, logged in the section's own table:
        R1 panel red-team (does it score?) → R2 experienced human (what only experience sees)
        → R3 final read (cross-section consistency, format, no [⚠VERIFY] left)
- [ ] 7. Run the strict mechanical gate → `Skill(engagement-os:eng-check)` in strict mode.
- [ ] 8. ONLY AFTER IT PASSES, render → `Skill(engagement-os:eng-render)` with the bid profile.
        It strips internal scaffolding and re-checks page counts. Do not assemble by hand here.
- [ ] 9. Verify the actual rendered artefact, then freeze that exact verified submission package
        to 4_final/ + record date; matrix fully closed
- [ ] 10. After all affected sections pass review and the new artefact is verified, checkpoint
         through `Skill(engagement-os:eng-propagate-change)`. A later edit is measured against
         this exact reconciled state.
```

**Watch the `scoring` line.** A section marked **per item** needs self-contained answers per item —
six deliverables scored out of 30 each means six complete answers, and a flowing narrative that
blurs them loses marks six times over.

**Page budgets: per-question or shared?** "Max 5 A4 for 3 questions" is a shared budget; "max 3 A4
per question response" is not. Confusing them always errs toward writing too much.

**Measure the budget in pages, mid-flight, before anything is approved.** The only build that
measures the *submission* page count is the one the gate refuses until every section is approved —
so measure a single section on its own, with the strip applied:

```
python3 .../render_document.py --sections <a dir holding just that section> \
    --out /tmp/pb --name s513 --to pdf --profile bid --force
```

`--force` here is legitimate and it reports everything it overrides (open `[⚠VERIFY]`, unapproved
status) as advisories. The internal review copy is rendered with `--profile plain`, which keeps the
scaffolding — its page count is NOT the buyer's page count.

**Under-use costs marks too.** "The level of detail provided" is an explicit scoring dimension, so
half an unused page budget on a 100+-mark criterion is marks left on the table. Lint warns in both
directions (`section-overlength` / `section-underlength`); the call is yours, but make it a call.

**Requirement-driven, not narrative-driven.** The response is assembled from the compliance
matrix; when every row is `met` and every mandatory satisfied, it's complete. The matrix is the
fact base; the response adds the persuasion.

**Match the buyer's format exactly** — volume split, page/word limits, mandated forms. Format
non-compliance is a common auto-reject; don't impose our own structure. The mandated format is a
**fact from the RFT**, so record it in the outline's `## Submission format (machine-checked)` table
(volumes · accepted file formats · paper · minimum font · separator pages). `eng_lint.py` reads it:
an artefact built in a format the buyer does not accept is an error under `4_final/`, and a
declared volume with no sections is reported. Otherwise the required format reaches the build only
through whatever someone types on the command line — a tender that demands Word would accept a deck
without a word of protest.

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
