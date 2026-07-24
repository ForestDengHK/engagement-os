# Building deliverables from findings

How an as-is assessment and the to-be / recommendation deliverables get assembled from
validated findings — without re-pasting evidence and without losing provenance.

## Contents
- The core move: findings are deliverable-neutral
- As-is (D1) assembly
- To-be (D2/D3/D4) derivation
- Versioning and the current-file index
- The panel gate
- Cross-cutting guardrails

## The core move: findings are deliverable-neutral

Because a finding is a fact baseline (not a recommendation), each deliverable pulls the
findings it needs and adds its *own* so-what. The evidence lives once, in the finding; the
deliverable adds narrative and interpretation on top. Findings declare `Feeds: D1 · D2 …`
so a deliverable can assemble itself by pulling every finding tagged for it.

## As-is (D1) assembly

1. Pull every finding with `Feeds: D1`; group by backbone item.
2. For each, lift its headline paragraph + severity; add D1's own cross-finding so-what.
3. Admit **only validated** facts into client-facing text. Keep `[⚠VERIFY]` items out of
   headlines — carry them as "open / pending" if at all.
4. Preserve cross-finding reconciliations (e.g. two conflicting maturity scores) as explicit
   narrative, not a silent choice.
5. The assessment is a *synthesis* of validated findings, not new analysis.

## To-be (D2/D3/D4) derivation

To-be docs derive from as-is **+ external research + prior-engagement experience**, but stay
tethered to the same fact base and precedence tags.

1. Start from each finding's **Remediation direction** cause-tag, not the raw problem.
2. Combine with external research (target-platform patterns) and prior experience; keep every
   derived claim tethered to a source-tagged fact.
3. Inherit only from **clean-reference** inputs (per the precedence register's clean-vs-stale
   map); re-base any stale derived doc first.
4. Carry the precedence tags into the deliverable so a reviewer can trace any recommendation
   back to a T1/T2 fact.

Where research is needed (e.g. a target platform's replication options, a regulatory matrix),
run it as a scoped research pass and record sources — the same provenance discipline applies
to *our* research as to client material.

## Versioning and the current-file index

- Version openly: `SKELETON → v0.1 → v0.2 … → v1.0 (client-issued) → v2.x (post-feedback)`.
- A `SKELETON` is structure-only — it holds no real content (names / € / dates). That is the
  content deck's job (v0.5+).
- Client deliverables stay **editable** (native shapes/text), never a stitched image-per-slide;
  figures-as-images go *inside* native slides.
- Update `DELIVERABLES.md` the moment a new version is produced; move the prior version to
  `archived/superseded_decks_<DATE>/` — never delete.

## The panel gate

- **Before building**, convene `panel-discuss` at a structure/decision fork to lock the
  deliverable's shape (e.g. the roadmap horizon structure, the exec-summary spine).
- **Before shipping**, run `panel-review` as the hard red-line gate: multi-role critique with
  a red-line pre-pass (each reviewer's red-lines checked as claim-contradiction / required
  omission / missing section, severity-tagged). No deliverable ships un-red-lined.
- **After workshops**, `panel-debrief` feeds the findings pipeline.

## Cross-cutting guardrails

- Provenance travels with the claim; superseded material stays citable-but-marked.
- No client-facing headline rests on an unverified figure.
- Deliverable-neutral findings mean each deliverable owns its so-what — don't bake a
  recommendation back into a finding.
- Apply the engagement's client-facing content rules (framing, no internal scaffolding on the
  slide face, plain language, benchmark-universe discipline, template matching) — these live in
  the project's CLAUDE.md "ALWAYS apply" block.
