---
name: eng-update-canonical
description: Use after eng-ingest-source runs, when facts change, or when the user says "update the canonical", "fold this into the summary", "refresh the reference summary/insights", or "roll up the new doc".
---

# Updating canonical

Consolidate the facts and interpretation from newly-ingested markdown into the canonical set so
a reader can trust "read the summary once, don't re-read the sources." This is the **only** skill
allowed to edit the canonical summaries.

## The two canonical files
- `_md/00_REFERENCE_SUMMARY.md` — **facts** (verifiable statements + `§Page/Slide` citations).
- `_md/01_REFERENCE_INSIGHTS.md` — **interpretation** (meaning, and deltas vs the brief/prior sources).

Facts and interpretation never mix across the two files.

## Workflow

```
Canonical Update Progress:
- [ ] 1. Read the new MD(s) / ingest report
- [ ] 2. Extract two streams: facts (cited) and interpretation
- [ ] 3. Route facts → 00_SUMMARY (right section, inline citation each)
- [ ] 4. Route interpretation → 01_INSIGHTS (per-source analysis + brief-vs-reality deltas)
- [ ] 5. Handle conflicts (supersede, never overwrite) + register [⚠VERIFY]
- [ ] 6. Bump dated "Updated:" headers; refresh open questions; trim for signal
```

**Step 3 — facts → `00_SUMMARY`.** Place each fact in the right numbered section; every
non-trivial fact carries an inline `source.md §Page N` citation. If it refines an existing fact,
**edit in place** and note it in the dated "Updated:" line — don't append a contradictory duplicate.

**Step 4 — interpretation → `01_INSIGHTS`.** Add per-source analysis (purpose / core argument /
the single most useful thing to cite) and any brief-vs-reality delta. Touch the TL;DR
"things that change how we run the engagement" list only when the doc genuinely shifts the engagement.

**Step 5 — conflicts (provenance discipline).** When a new source contradicts an existing one,
do NOT silently overwrite: keep both, mark the weaker/older `⚠ superseded-by <newer>`, and add a
row to the source-precedence register (`_pm/source_precedence_and_conflict_register.md`) with the
tier tags. Facts you can't yet verify get a `[⚠VERIFY]` marker + a register row stating what closes them.

**Step 6 — keep it lean.** Bump the dated "Updated:" header summarizing what this pass added;
refresh the open-questions section. If a doc is generic or fully superseded, record it in the
manifest and keep it OUT of the canonical narrative — depth lives in the per-topic MDs.

## Optional batch pass
After several ingests, run a corpus-wide reconciliation: re-check read-order, resolve internal
contradictions, confirm every canonical claim still traces to a live MD.

## Conventions
Facts-vs-interpretation detail: `eng-os` → `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/canonical-reference.md`.
Precedence tiers + `[⚠VERIFY]` lifecycle: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/provenance-and-precedence.md`.

## Anti-goals
No document conversion (that's `eng-ingest-source`); no new findings/analysis docs (that's
`eng-write-findings`); no editing of the source MDs' faithful content.
