# Playbook: a new source document (or batch) arrives

The most frequent loop in an engagement. Runs once per document; batch by repeating
the loop, not by widening a step. Each step names the skill that owns it — follow
that skill, don't reproduce it here.

## Chain

```
eng-ingest-source ─► eng-update-canonical ─► (findings impact?) ─► eng-maintain-memory
     per doc            per batch              conditional            per session
```

1. **Ingest — one doc at a time** → `eng-ingest-source`.
   Convert to anchored markdown with the lossless image rule; append the manifest row.
   Verify: output markdown exists under the reference pack, images triaged
   (decorative dropped / content kept+captioned / uncertain OCR'd inline), manifest row added.
2. **Repeat step 1 for every doc in the batch.** Do not start canonicalizing until the
   batch is fully ingested — canonical updates are cheaper in one pass.
3. **Canonicalize — once per batch** → `eng-update-canonical`.
   Facts → `00_REFERENCE_SUMMARY.md`; interpretation → `01_REFERENCE_INSIGHTS.md`;
   conflicts superseded, never deleted; new `[⚠VERIFY]` items registered.
   Verify: every ingested doc is reflected in the canonical set with provenance tags.
4. **Findings impact check — judgment gate, no skill.**
   Ask: does any new fact create, extend, or contradict a finding?
   - Yes → invoke `eng-write-findings` (new finding or extend an existing one, with the
     new source cited). Contradiction → stamp the losing claim `⚠ superseded-by`, keep both.
   - No → note "no finding impact" in the engagement log and stop.
5. **Log + memory — once per session** → `eng-maintain-memory`.
   Engagement-log entry (what arrived, what it changed, what's still owed);
   update open-question backlog statuses the new evidence answers.

## Stop gates

- **STOP after step 3** if the batch is reference-only (background reading with no
  engagement facts) — steps 4–5 collapse to a one-line log entry.
- **STOP and surface to the human** if a new fact contradicts a *validated* finding
  that already fed a shipped deliverable — that's a deliverable erratum decision, not
  a routine update.
