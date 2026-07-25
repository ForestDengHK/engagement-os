---
name: eng-build-deliverable
description: Use when the user says "build D1/D2/…", "draft the assessment", "put the deliverable together", or "turn the findings into the report" — i.e. when assembling a client deliverable from validated findings. (Rendering the finished content into a deck/document FILE is eng-render.)
---

# Building deliverables

Assemble a deliverable from **validated** findings without re-pasting evidence. Findings are
deliverable-neutral fact baselines; each deliverable adds its own so-what on top.

## Prerequisite
Findings must have been swept by `eng-validate-findings` — build only from reconciled inputs (the
clean-reference layer). Method detail: `eng-os` → `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/deliverable-build.md`.

**If missing:** findings exist but were never validated → run `eng-validate-findings` first;
building from unreconciled inputs bakes contradictions into an artefact that carries our name.

## Pick the mode

Match the deliverable's KIND against the mode table in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/deliverable-build.md` (Assembly / Derivation /
Curation). The table, not a hardcoded fork, is the taxonomy — a deliverable that fits no row
gets a new row there, not a forced fit.

## Build

Follow the method for that mode in the reference — its step lists live there, not here.
Non-negotiables at this desk, whichever mode:
- Admit ONLY validated facts into client-facing text; `[⚠VERIFY]` stays out of headlines.
- A `SKELETON` holds no real content (names / € / dates); the deliverable stays **editable**
  (native shapes/text, never a stitched image-per-slide).
- Version openly and update `DELIVERABLES.md` the moment a version exists; archive the prior.

## The review gate (not optional)
The gate itself is mandatory; the tool is the Panel Framework **if installed**.
- **Before building**, `panel-discuss` at the structure fork to lock the deliverable's shape.
- **Before shipping**, `panel-review` as the hard red-line gate — no deliverable ships un-red-lined.
- **After workshops**, `panel-debrief` feeds the findings pipeline.
- **If the `panel-*` skills are not installed**, run a manual multi-lens review instead (walk the
  deliverable from the client-sponsor, solution-architect, security/compliance, and quality angles
  and red-line each) — never ship without *some* multi-perspective review.

**Producing the file is a separate step** — hand off to the `eng-render` skill with
`--profile deliverable`. It owns discover/gate/strip/measure and routes the rest to
`presentation-builder` (deck) or the `docx` skill (document). Build the content here; render there.

## Guardrails
No client-facing headline rests on an unverified figure. Provenance travels with the claim.
Don't bake a recommendation back into a finding. Apply the project's CLAUDE.md "ALWAYS apply"
client-facing content rules (framing, no internal scaffolding on the slide face, plain language,
benchmark-universe discipline, template matching).
