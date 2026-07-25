---
description: Findings are ready and a deliverable is due — validate the corpus, lock the structure with a panel, build it, pass the red-line review gate, then rev the live-file index.
---

Run the **deliverable-sprint** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/deliverable-sprint.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: which deliverable (e.g. `D1`), and its due date if it drives scope.

Order is not optional: **validate before building** (a deliverable built on unvalidated findings
inherits every unresolved conflict), and the review gate clears before anything ships. When the
version lands, update the live-file index and archive the old version — never delete it.
