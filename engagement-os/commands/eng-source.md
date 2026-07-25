---
description: A new source document or batch arrived — bucket it by constraint, ingest to citable markdown, canonicalize per bucket, check findings impact, log it.
---

Run the **new-source-arrived** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/new-source-arrived.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: the path(s) to the incoming document(s).

Step 0 is bucketing by **how each document was obtained** (`public/` · `pre_award/` ·
`engagement/`; the tender pack itself goes to `01_pursuit/<ENG-ID>/1_received/`). A mixed batch
splits into per-bucket sub-batches. If provenance is unclear, ask — do not default to the least
restrictive bucket.
