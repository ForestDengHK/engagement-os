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
show or delegate its script command to the user. It reports two lists, because two kinds of
material show up and they have different destinations:

- **to INGEST** — sourced material with no markdown yet → run this playbook over it.
- **to INDEX** — our own assets under `01_pursuit/_shared/` with no row in `firm_assets.md`
  → these are never converted and never bucketed; invoke
  `Skill(engagement-os:eng-index-assets)`.

Show both lists, confirm, then route each to the right place. The user should never have to
remember which command an arriving file needs — that is what the scan is for.

**Agent-only implementation:** the scan is provided by
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/convert_source.py`. It is an implementation detail
behind this command, not a user entry point.

Step 0 is bucketing by **how each document was obtained** (`public/` · `pre_award/` ·
`engagement/`; the tender pack itself goes to `01_pursuit/<ENG-ID>/1_received/`). A mixed batch
splits into per-bucket sub-batches. If provenance is unclear, ask — do not default to the least
restrictive bucket.
