---
name: eng-ingest-source
description: Use when a new client- or research-supplied document (pdf, docx, pptx/ppsx, xlsx, csv, png/screenshot) arrives from the client, when the user says "ingest this doc", "convert this deck to markdown", "add this to the reference pack", or "a new source came in".
---

# Ingesting sources

Convert exactly one source document into a faithful, lossless, citable markdown file under
`_shared/<client>_reference/_md/`, register it in the manifest, and hand off. This skill is
**per-document and additive** — it does NOT edit the canonical summaries (that's `eng-update-canonical`).

## Where things go
Paths below are under the reference-pack root `02_delivery/_shared/<client>_reference/`.
- Originals: place under a **source subfolder** you create, e.g. `<pack-root>/<source-group>/<file>` — the client's own naming; **never renamed or edited**. (`eng-scaffold` drops a `SOURCES_GO_HERE.md` stub in the pack root as the reminder.)
- Derived markdown → `<pack-root>/_md/<NN_topic>/<slug>.md`.
- Extracted images → `<pack-root>/_md/images/<topic>/`.

## Workflow

```
Ingest Progress:
- [ ] 1. Settle the original under the reference pack; record md5
- [ ] 2. Dedup guard (md5 vs manifest) — stop if byte-identical
- [ ] 3. Convert to markdown (run convert_source.py)
- [ ] 4. Triage every extracted image; OCR the uncertain ones inline
- [ ] 5. Register the manifest row in _md/README.md
- [ ] 6. Emit an ingest report; point to eng-update-canonical
```

**Step 2 — dedup guard.** md5 the source and grep `_md/README.md` (manifest + "What was NOT
converted"). If byte-identical to an existing source, stop and log it as a duplicate — don't
convert twice.

**Step 3 — convert (deterministic extraction):**
```bash
# Pass FULL paths from the repo root so output lands in the real reference pack, not CWD.
PACK=02_delivery/_shared/<client>_reference
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/convert_source.py <source_path> \
  --out "$PACK/_md/<NN_topic>/<slug>.md" --images-dir "$PACK/_md/images/<topic>"
```
Handles pdf/pptx/docx/xlsx/csv/image with per-`## Page N:` / `## Slide N:` anchors and image
extraction. If a library is missing it prints a `pip install` line for that format — install
and re-run. For docx/xlsx you may prefer the `docx` / `xlsx` skills for tricky files.

**Step 4 — image triage (the lossless rule; agent + vision).** For every image the script
extracted (all emitted tagged `[uncertain]`), classify:
- `[decorative]` (logo/border/background) → delete the file + remove the line.
- `[content]` (a meaningful diagram/table) → keep; write a caption from surrounding text.
- `[uncertain]` → **OCR inline** into a `<details><summary>OCR extracted text</summary>…</details>`
  block, then retag `[ocr-done]`. **Never delete an `[uncertain]` image before its text is captured.**

**Step 5 — register** the row in `_md/README.md`: `source file → md → pages/slides → topic → notes`.
If it's a new topic, create the `NN_topic/` folder + a manifest sub-table.

**Step 6 — ingest report** (stdout, for the next stage): what was converted, page/slide count,
images kept / OCR'd / dropped, and any new open questions spotted. Then point to `eng-update-canonical`.

## Edge cases
- **Multi-file pack:** loop — one MD per file, never merge.
- **Our own analysis** is not a client source — keep as-is and flag; don't ingest into the SOURCE tier.
- **Superseded version:** keep the old MD, mark `⚠ Superseded by <newer>`; never delete.
- **Confidential:** carry the CONFIDENTIAL marker into the MD header.

## Conventions
Full ingestion + image-rule detail: the `eng-os` skill, `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/canonical-reference.md`.

## Anti-goals
No summarizing into canonical files (that's `eng-update-canonical`); no interpretation/deltas; no
renaming/altering originals; no lossy image deletion.
