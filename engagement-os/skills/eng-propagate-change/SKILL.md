---
name: eng-propagate-change
description: >-
  Use when a reviewer or user has edited an engagement artefact after it was generated,
  reviewed, approved, rendered, or frozen; when the user says "I changed the estimate",
  "the reviewer edited this section", "sync this change", "what does this affect", "propagate
  this downstream", "re-open anything impacted", or "I changed a file after everything ran";
  and automatically before checking, rendering, or freezing an engagement. Detects changed
  scope, requirements, evidence, research, estimate workbooks, response sections, figures,
  generated outputs, and frozen packages; refreshes deterministic derivatives through their
  owning skills, sends judgement-bearing content back to review, and never overwrites history.
---

# Propagating a reviewed change

Make a manual edit visible everywhere it matters without rebuilding unrelated work or silently
changing a submitted package. The user names the edit in conversation; never ask them to run a
script or remember the downstream chain.

The dependency baseline is `_pm/change_impact_state.json`. It is machine-maintained and records
hashes, not content. The engine is
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/change_impact.py`.

## The three propagation rules

1. **Regenerate deterministic projections.** Formula caches, `estimation.md`, figure exports and
   rendered files are refreshed through the skill that owns them.
2. **Invalidate judgement; never silently rewrite it.** A changed requirement, evidence row,
   research row, estimate, section or figure moves every affected reviewed section back to
   `revise-r2` (or `revise` for delivery) and records why. It must pass human review again.
3. **Never mutate history.** Anything under `4_final/` is immutable. An upstream change creates a
   new version; a direct edit to a frozen file is an error to reconcile, not a new baseline.

Generated artefacts do not flow upstream. A reviewer edit made directly in DOCX/PDF or an
`estimation.md` snapshot must first be reconciled into its maintained source (section markdown,
figure HTML/PPTX, or `estimation.xlsx`), then regenerated.

## Workflow

```
Change Propagation:
- [ ] 1. Scan against the last reconciled checkpoint; show changed files and entity IDs
- [ ] 2. If no checkpoint exists, inspect current state and establish one only after confirming
        it is reconciled — never claim to know what changed before the first baseline
- [ ] 3. Apply mechanical invalidation: reviewed/approved affected sections → revise
- [ ] 4. Route every deterministic refresh through its owning skill
- [ ] 5. Route judgement-bearing impacts to the owning skill + human review
- [ ] 6. Render and verify again when a delivered file is affected
- [ ] 7. After all impacts and reviews are resolved, checkpoint; then run eng-check strict
```

**Step 1 — report before mutation.** Run the engine's normal scan internally. Read back:
changed files, changed `R-`/`S-`/`A-`/`BR-` entities, affected sections, required status, owner,
and whether a frozen package exists. A filesystem save is not a workflow event until this scan
runs; this skill is also invoked automatically by the downstream gates below.

**Step 3 — apply only invalidation.** Use the engine's apply mode. It may change lifecycle
status and append a change-impact `revise` row to the review log. It must not rewrite the
section's argument, estimate, evidence, or final file.

**Steps 4–5 — explicit hand-offs.** Names below that are not `engagement-os:*` belong to
companion skills, whose invocation name depends on how they were installed: bare when
personal, namespaced under the plugin that ships them (`document-skills:xlsx`,
`deck-craft:designing-figures`) when from one. If the bare name is not in your skill list,
use the namespaced form — `eng-check companions` prints it for this machine.

- `estimation.xlsx` or S-ID change →
  `Skill(engagement-os:eng-estimate)`; that skill invokes `Skill(xlsx)`, recalculates, verifies
  formulas, and refreshes `estimation.md`.
- `rfp_analysis.md` / compliance R-ID change →
  `Skill(engagement-os:eng-rfp-analyze)`, then only the sections whose `answers_reqs` or
  `depends_on` intersect the change.
- A-ID change → `Skill(engagement-os:eng-index-assets)`.
- BR research-row change → `Skill(engagement-os:eng-bid-research)`.
- Response section or its dependency changed →
  `Skill(engagement-os:eng-bid-respond)` for the affected files only, followed by the human
  review round.
- Figure source changed → `Skill(designing-figures)` to regenerate PNG + editable PPTX, then
  re-review every section declaring that F-ID.
- Rendered DOCX/PDF/PPTX changed directly → reconcile its edits into the maintained sources,
  then `Skill(engagement-os:eng-render)`.
- Before a new final version → `Skill(engagement-os:eng-check)` strict, render, verify the
  actual artefact, and freeze a new version without touching the old one.

## Dependency declarations

Existing section frontmatter already provides most of the graph:

- `answers_reqs: [R-nnn]` → compliance rows
- `evidence: [A-nnn]` → firm-asset rows
- `figures: [F-nn]` → figure sources/exports
- body references such as `log #3` → `BR-003`
- `depends_on: [...]` → additional load-bearing dependencies, especially
  `estimation.xlsx`, S-IDs, or a named analysis file

Do not add `depends_on` for decorative context. It means: changing this dependency invalidates
the section's existing review.

## Checkpoint contract

A checkpoint means all listed changes have been propagated and every affected judgement has the
required current review. Never checkpoint merely to silence the report. Write it only after that
work is complete, report how many files and sections it covers, then run strict
`Skill(engagement-os:eng-check)`. If the strict check causes another tracked edit, propagate and
checkpoint that change before freezing.

The engine refuses to checkpoint error-severity states: a modified/deleted frozen file, a
generated output edited without any maintained source change, an edited estimate snapshot without
its workbook, or unreadable state. This prevents "accept current state" from becoming an override.

Create the first checkpoint at the end of `eng-new`, before substantive work starts. Refresh it
after a clean review/render/freeze cycle. Do not store source text in the state file.

## Agent-only implementation

The engine has scan, apply and checkpoint modes. Run them yourself and translate the JSON or text
report into plain language. Never expose its Python invocation as the user interface.

## Guardrails

- Do not rebuild unrelated sections. Use declared IDs and paths to bound the impact.
- Do not infer that a changed file is approved merely because it exists.
- Do not copy edits out of a generated snapshot into a maintained source without showing the
  user what changed.
- Do not checkpoint with unresolved impacts, failed checks, or pending human review.
- Never overwrite or re-baseline a modified frozen file.
