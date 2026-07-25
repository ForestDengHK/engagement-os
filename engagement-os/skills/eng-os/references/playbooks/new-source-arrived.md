# Playbook: a new source document (or batch) arrives

The most frequent loop in an engagement. Runs once per document; batch by repeating
the loop, not by widening a step. Each step names the skill that owns it — follow
that skill, don't reproduce it here.

## Chain

```
eng-ingest-source ─► eng-update-canonical ─► (findings impact?) ─► eng-maintain-memory
     per doc            per batch              conditional            per session
```

0. **Bucket the batch first — by how each doc was obtained**, not by topic.
   Public → `_sources/public/` · buyer-issued pre-award → `_sources/pre_award/` ·
   client-handed post-award → `_sources/engagement/` · the tender pack itself →
   `01_pursuit/<ENG-ID>/1_received/`. A mixed batch splits into per-bucket sub-batches
   and each runs the loop separately. If a doc's provenance is unclear, ask — don't default.
1. **Ingest — one doc at a time** → `eng-ingest-source`.
   Convert to anchored markdown with the lossless image rule; append the manifest row.
   Verify: output markdown exists under the right bucket, images triaged
   (decorative dropped / content kept+captioned / uncertain OCR'd inline), manifest row added.
2. **Repeat step 1 for every doc in the sub-batch.** Do not start canonicalizing until the
   sub-batch is fully ingested — canonical updates are cheaper in one pass.
3. **Canonicalize — once per sub-batch, into that bucket's pair** → `eng-update-canonical`.
   Facts → `<bucket>/_md/00_REFERENCE_SUMMARY.md`; interpretation →
   `<bucket>/_md/01_REFERENCE_INSIGHTS.md`; conflicts superseded, never deleted; new
   `[⚠VERIFY]` items registered. **Never fold one bucket's facts into another's summary.**
   Verify: every ingested doc is reflected in its own bucket's canonical set with provenance tags.
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
- **STOP before citing across buckets.** An `engagement/` fact never enters a bid document;
  a `pre_award/` fact carried into delivery stays `[T3]` until re-established from a
  delivery-phase source or measured from the system. Cross-bucket reasoning goes in
  `_pm/source_precedence_and_conflict_register.md`, nowhere else.
