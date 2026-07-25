---
description: The scope grew — add a block to an existing engagement repo (bid won, study became the engagement, client tendered). Re-scaffold, top up CLAUDE.md, write the handoff, re-baseline sources.
---

Run the **adding-a-block** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/adding-a-block.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: which block is being added, and the repo root.

Three things this is NOT allowed to shortcut:
1. `--mode` must name the **old blocks and the new one** — it's the repo's full block list, not a delta.
2. The handoff artefact gets written **before** any new-block work starts.
3. Sources are re-baselined: winning verifies nothing, and `engagement/` material never enters a bid.

You own the `CLAUDE.md` top-up and the handoff draft — produce them and ask for
confirmation. Do not tell the user to go edit a file.
