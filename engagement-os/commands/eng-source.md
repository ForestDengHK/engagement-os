---
description: A new source document or batch arrived — bucket it by constraint, ingest to citable markdown, canonicalize per bucket, check findings impact, log it.
---

Run the **new-source-arrived** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/new-source-arrived.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments: `$ARGUMENTS`

**With a path** — ingest that document.

**With no arguments — do not ask which file. Find them.** Run the source scan internally; never
show or delegate its script command to the user. It reports four lists, because material
arrives in kinds with different destinations — and because a file that was dealt with once can
stop being dealt with:

- **to INGEST** — sourced material with no markdown yet → run this playbook over it.
- **to CONVERT** — our own assets under `01_pursuit/_shared/` with no markdown under
  `_shared/_md/` → assets get the same md-first treatment as sources; the md is the working
  text for analysis and page-level citation.
- **to INDEX** — our own assets with no row in `firm_assets.md` → invoke
  `Skill(engagement-os:eng-index-assets)` (its step 0 converts, so the two lists are usually
  dealt with in one run).
- **to RE-INDEX** — assets whose markdown changed *after* their row was written → invoke
  `Skill(engagement-os:eng-index-assets)` for those rows only. Image triage puts what the
  diagrams prove into the markdown, and it usually lands long after the row was drafted: a
  row written from an untriaged conversion says what the prose said and nothing the figures
  showed. Nobody updates these by hand, because nobody knows they went stale.

Show the lists, confirm, then route each to the right place. The user should never have to
remember which command an arriving file needs — that is what the scan is for.

**Agent-only implementation:** the scan is provided by
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/convert_source.py`. It is an implementation detail
behind this command, not a user entry point.

Step 0 is bucketing by **how each document was obtained** (`public/` · `pre_award/` ·
`engagement/`; the tender pack itself goes to `01_pursuit/<ENG-ID>/1_received/`). A mixed batch
splits into per-bucket sub-batches. If provenance is unclear, ask — do not default to the least
restrictive bucket.
