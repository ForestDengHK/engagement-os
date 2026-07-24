---
name: eng-build-deliverable
description: Use when the user says "build D1/D2/…", "draft the assessment", "assemble the target-architecture deck", "put the deliverable together", or "turn the findings into the report" — i.e. when assembling a client deliverable from validated findings.
---

# Building deliverables

Assemble a deliverable from **validated** findings without re-pasting evidence. Findings are
deliverable-neutral fact baselines; each deliverable adds its own so-what on top.

## Prerequisite
Findings must have been swept by `eng-validate-findings` — build only from reconciled inputs (the
clean-reference layer). Method detail: `eng-os` → `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/deliverable-build.md`.

## Pick the mode

**Determine which you're building:**
- **As-is (assessment)?** → Assembly mode below.
- **To-be / target / roadmap / cost / exec-summary?** → Derivation mode below.

### As-is assembly
```
- [ ] 1. Pull every finding with Feeds: <D-item>; group by backbone item
- [ ] 2. For each, lift its headline paragraph + severity; add the deliverable's own so-what
- [ ] 3. Admit ONLY validated facts; keep [⚠VERIFY] items out of headlines
- [ ] 4. Preserve cross-finding reconciliations as explicit narrative, not silent choices
- [ ] 5. Version openly; update DELIVERABLES.md; archive the prior version
```
The assessment is a *synthesis* of validated findings, not new analysis.

### To-be derivation
```
- [ ] 1. Start from each finding's Remediation direction cause-tag (not the raw problem)
- [ ] 2. Combine with external research (target-platform patterns) + prior experience
- [ ] 3. Keep every derived claim tethered to a source-tagged fact
- [ ] 4. Inherit only from clean-reference inputs; re-base any stale derived doc first
- [ ] 5. Carry precedence tags through so any recommendation traces back to a T1/T2 fact
```
Where research is needed, run a scoped research pass and record sources — the same provenance
discipline applies to our research as to client material.

## The review gate (not optional)
The gate itself is mandatory; the tool is the Panel Framework **if installed**.
- **Before building**, `panel-discuss` at the structure fork to lock the deliverable's shape.
- **Before shipping**, `panel-review` as the hard red-line gate — no deliverable ships un-red-lined.
- **After workshops**, `panel-debrief` feeds the findings pipeline.
- **If the `panel-*` skills are not installed**, run a manual multi-lens review instead (walk the
  deliverable from the client-sponsor, solution-architect, security/compliance, and quality angles
  and red-line each) — never ship without *some* multi-perspective review.

## Versioning + format
`SKELETON → v0.1 → v0.2 … → v1.0 (client-issued) → v2.x`. A `SKELETON` holds no real content
(names / € / dates) — that's the content deck's job. Client deliverables stay **editable**
(native shapes/text), never a stitched image-per-slide; figures-as-images go inside native slides.
Update `DELIVERABLES.md` the moment a version is produced; move the prior to
`archived/superseded_decks_<DATE>/`.

## Guardrails
No client-facing headline rests on an unverified figure. Provenance travels with the claim.
Don't bake a recommendation back into a finding. Apply the project's CLAUDE.md "ALWAYS apply"
client-facing content rules (framing, no internal scaffolding on the slide face, plain language,
benchmark-universe discipline, template matching).
