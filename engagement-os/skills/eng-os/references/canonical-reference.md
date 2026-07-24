# Ingestion & canonical-reference conventions

How raw client materials become a trustworthy, citable knowledge base — and stay lean.

## Contents
- The two-directory, two-file-class pattern
- The five load-bearing rules
- The lossless image / OCR rule (the key discipline)
- Why canonical = multiple files, not one mega-file
- The new-document flow
- Facts vs interpretation: what goes where

## The two-directory, two-file-class pattern

```
_shared/<client>_reference/          ← SOURCE tier (originals, never edited)
  Data Strategy/…pdf                 ← kept in the client's own folder taxonomy
  DWH Documents/…pptx
  _md/                               ← DERIVED tier (all generated markdown)
    README.md                        ← the manifest: source→md map + conventions
    00_REFERENCE_SUMMARY.md          ← CANONICAL facts (one comprehensive summary)
    01_REFERENCE_INSIGHTS.md         ← CANONICAL interpretation (deltas vs the brief)
    01_topic/ … NN_topic/            ← per-topic numbered folders, one MD per source
    images/<topic>/                  ← extracted rasters + full-page renders
```

## The five load-bearing rules

1. **Source → derived separation.** Originals stay untouched under the client's own folder names; every generated `.md` lives under `_md/`. Provenance = the derived file always names its source path + page count, both in the README row and in its own header.
2. **One MD per source file**, with `## Page N:` / `## Slide N:` anchors, so any downstream claim can cite `file.md §Page 12`.
3. **Lossless image rule** (see next section) — no information lost, but noise stripped.
4. **Canonical = multiple files split by kind**, not one mega-file (see below).
5. **New-document flow is fixed** (see below): drop original → convert to MD in the matching `_md/` group → add a README row → fold facts/deltas into SUMMARY/INSIGHTS.

## The lossless image / OCR rule (the key discipline)

Every extracted image is triaged into exactly one of three buckets:

- **`[decorative]`** → delete (logos, borders, backgrounds, spacers). No information lost.
- **`[content]`** — a diagram/table that carries meaning and survived text extraction → keep as a captioned PNG render under `images/<topic>/`; write the caption from the surrounding text, not the filename.
- **`[uncertain]`** → **OCR the image inline** into a collapsible block, then retag `[ocr-done]`:
  ```markdown
  <details><summary>OCR extracted text — figure 3, slide 12</summary>

  ...verbatim OCR text...
  </details>
  ```

**The rule that makes it lossless:** *if a human could not be certain the image is decorative, its text is OCR'd into the MD before the image may be dropped.* Never delete an `[uncertain]` image before its text is captured. This is what lets a reader trust "read the MD, don't re-open the source."

## Why canonical = multiple files, not one mega-file

- `00_…SUMMARY` = **raw facts** — "read this once, don't re-read the sources."
- `01_…INSIGHTS` = **interpretation / deltas vs the brief** — "how to *use* the facts."
- per-topic MDs = **citation depth** — reach only when you need to quote.

Multi-file wins because: independent update cadence, smaller diffs, targeted grep, and a stable read-order (`README → SUMMARY → INSIGHTS → source MD`) that mirrors how much detail the reader actually needs. A single mega-file rots and can't be updated without a giant diff.

## The new-document flow

1. Drop the original into the best-fit sibling **source** folder (the client's own naming; don't rename originals). Record its md5.
2. **Dedup guard:** md5 the source and check the README manifest — if byte-identical to an existing source, stop and log it as a duplicate; do not convert twice.
3. Convert to one MD in the matching `_md/<topic>/` group, with page/slide anchors, tables as markdown tables, and image triage applied.
4. Add/refresh the manifest row in `_md/README.md`.
5. Fold facts → `00_SUMMARY` and interpretation → `01_INSIGHTS`, preserving citations; bump the dated "Updated:" header; refresh open questions.

Steps 1–4 are `eng-ingest-source`; step 5 is `eng-update-canonical` — the only skill allowed to edit the canonical summaries.

## Facts vs interpretation: what goes where

- A **fact** is a verifiable statement + its `§Page/Slide` citation → `00_SUMMARY`. Every non-trivial fact carries an inline citation. If a new source refines an existing fact, edit in place and note it in the dated "Updated:" line — don't append a contradictory duplicate.
- An **interpretation** is what a fact *means*, or where it conflicts with the brief or a prior source → `01_INSIGHTS`. Update the TL;DR "things that change how we run the engagement" list only when a doc genuinely shifts the engagement.
- **Conflict handling:** when a new source contradicts an existing one, do not silently overwrite — keep both, mark the weaker/older `⚠ superseded-by <newer>`, and (if the engagement uses one) add a row to the source-precedence register. Facts that can't yet be verified get a `[⚠VERIFY]` marker with what's needed to close them. See `provenance-and-precedence.md`.

## Edge cases
- **Our own analysis is not a client source.** Documents *we* authored are kept as-is and flagged; they are not ingested into the SOURCE tier.
- **Multi-file packs:** loop and convert each file to its own MD — do not merge a multi-document pack into one MD.
- **Superseded versions:** keep the old MD, mark `⚠ Superseded by <newer>`; never delete.
- **Confidential-flagged docs:** carry the CONFIDENTIAL marker into the MD header.
- **Trim for signal:** if a doc is generic or fully superseded, record it in the manifest and keep it out of the canonical narrative — canonical stays lean.
