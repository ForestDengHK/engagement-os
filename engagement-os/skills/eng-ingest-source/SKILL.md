---
name: eng-ingest-source
description: Use when a new client- or research-supplied document (pdf, docx, pptx/ppsx, xlsx, csv, png/screenshot) arrives from the client, when the user says "ingest this doc", "convert this deck to markdown", "add this to the reference pack", or "a new source came in".
---

# Ingesting sources

Convert exactly one source document into a faithful, lossless, citable markdown file under the
right `_sources/` bucket, register it in the manifest, and hand off. This skill is
**per-document and additive** — it does NOT edit the canonical summaries (that's `eng-update-canonical`).

## Pick the bucket FIRST
Buckets track the **constraint on the material** — who may see it and where we may use it — not
which phase we're in. Material under different constraints must not pool: it corrupts the evidence
chain (a pre-award assumption resurfaces as a verified client fact) and leaks restricted material
into later bids. Decide by **how the document was obtained**:

| How we got it | Bucket (`<pack-root>`) |
|---|---|
| Found in public — company info, sector/regulatory research, published benchmarks | `_sources/public/` |
| Issued or published by the buyer pre-award; market research around the tender | `_sources/pre_award/` |
| Handed to us by the client under this engagement's terms — including a standalone research assignment | `_sources/engagement/` |
| **The tender pack itself** (RFP + appendices) | `01_pursuit/<ENG-ID>/1_received/` — the contractual artefact, cited `[RFP §x]` |

If you can't tell, ask — **don't default to the least restrictive bucket**. Full boundary + flow
rules: the planted `_sources/README.md`.

## Where things go
Paths below are under the chosen `<pack-root>`.
- Originals: place under a **source subfolder** you create, e.g. `<pack-root>/<source-group>/<file>` — the client's own naming; **never renamed or edited**. (`eng-scaffold` drops a `SOURCES_GO_HERE.md` stub in each bucket as the reminder.)
- Derived markdown → `<pack-root>/_md/<NN_topic>/<slug>.md`.
- Extracted images → `<pack-root>/_md/images/<topic>/`.

## Workflow

```
Ingest Progress:
- [ ] 0. Choose the _sources/ bucket by provenance
- [ ] 1. Settle the original under that bucket; record md5
- [ ] 2. Dedup guard (md5 vs manifest) — stop if byte-identical
- [ ] 3. Convert to markdown (run convert_source.py)
- [ ] 4. Triage every extracted image; OCR the uncertain ones inline
- [ ] 5. Register the manifest row in <pack-root>/_md/README.md
- [ ] 6. Emit an ingest report; point to eng-update-canonical
```

**Step 2 — dedup guard.** md5 the source and grep the bucket's `_md/README.md` (manifest + "What
was NOT converted"). If byte-identical to an existing source, stop and log it as a duplicate —
don't convert twice. Check **only this bucket**: the same document legitimately appearing in two
buckets is a provenance fact, not a duplicate, and each bucket cites its own copy.

**Step 3 — convert (deterministic extraction):**
```bash
# Pass FULL paths from the repo root so output lands in the real bucket, not CWD.
PACK=_sources/<bucket>          # public | pre_award | engagement
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/convert_source.py <source_path> \
  --out "$PACK/_md/<NN_topic>/<slug>.md" --images-dir "$PACK/_md/images/<topic>"
```

For Word sources, a heading that already carries the buyer's clause number is preserved as a
native clause anchor (`## 2.1 Timetable` → `## §2.1 Timetable`). Only unnumbered headings receive
the synthetic `§Section N` fallback. Cite the native clause wherever it exists; page/section
fallbacks are for documents whose author supplied no stable numbering.
Handles pdf/pptx/docx/xlsx/csv/image with per-unit anchors (`## Page N:` pdf · `## Slide N:` pptx ·
`## Sheet:` xlsx · `## Section N:` docx). It walks grouped shapes and pulls speaker notes, and it
auto-drops images that are decorative by construction (repeated across units, or under 6KB),
reporting the counts. If a library is missing it prints a `pip install` line for that format.

The script **delegates extraction to the same tools the format skills use** — `pandoc` for docx,
`markitdown` for pptx (pdf/xlsx stay on pymupdf/openpyxl, which are what give per-page and
per-sheet anchors). It adds only the packaging: provenance header, citable anchors, image
policy. Each output names its extractor; if a tool is missing it falls back to the python
library and says in the header what that costs. Install both for faithful output:
`brew install pandoc` · `pip install markitdown`.

**When to escalate to the format skill anyway.** The script is bulk: deterministic, repeatable,
no token cost per document. Re-do a single document with the `pptx` / `docx` / `pdf` / `xlsx`
skill when the script's own output tells you it fell short:
- a page/slide renders as `_(no extractable text …)_` and its images don't explain it → scanned or vector-only, needs real OCR
- the doc is known to carry **tracked changes or comments** (a reviewed policy, a marked-up contract) — the script reads final text only
- **charts / SmartArt** whose meaning is in the data labels, not the shape text
- merged or nested tables that came out ragged
One re-done document is cheap; a whole batch through a skill is not. Escalate per document, not per batch.

**Step 4 — image triage (the lossless rule; agent + vision).** For every image the script
extracted (all emitted tagged `[uncertain]`), classify:
- `[decorative]` (logo/border/background) → delete the file + remove the line.
- `[content]` (a meaningful diagram/table) → keep; write a caption from surrounding text.
- `[uncertain]` → **OCR inline** into a `<details><summary>OCR extracted text</summary>…</details>`
  block, then retag `[ocr-done]`. **Never delete an `[uncertain]` image before its text is captured.**

**Step 5 — register** the row in `<pack-root>/_md/README.md`: `source file → md → pages/slides →
topic → notes`. If it's a new topic, create the `NN_topic/` folder + a manifest sub-table.

**Step 6 — ingest report** (stdout, for the next stage): what was converted, page/slide count,
images kept / OCR'd / dropped, and any new open questions spotted. Then point to `eng-update-canonical`.

## Edge cases
- **Multi-file pack:** loop — one MD per file, never merge.
- **Our own analysis** is not a source — keep as-is and flag; don't ingest into `_sources/` at all
  (it belongs in a work tree: `00_research/1_analysis/`, `01_pursuit/<ENG-ID>/2_analysis/`,
  or `02_delivery/_shared/`).
- **Superseded version:** keep the old MD, mark `⚠ Superseded by <newer>`; never delete.
- **Confidential:** carry the CONFIDENTIAL marker into the MD header.
- **Same doc, two buckets:** ingest into each bucket separately — do NOT cross-link or move. A
  `engagement/` copy must never become a `pre_award/` citation.
- **Wrong bucket, caught later:** move the original + its `_md/` output together, fix both
  manifests, and check whether anything already cited it across the boundary.

## Conventions
Full ingestion + image-rule detail: the `eng-os` skill, `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/canonical-reference.md`.

## Anti-goals
No summarizing into canonical files (that's `eng-update-canonical`); no interpretation/deltas; no
renaming/altering originals; no lossy image deletion.
