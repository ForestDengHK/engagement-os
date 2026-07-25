---
description: Bootstrap a new engagement repo — pick the block mode (research / pursuit / delivery / full), scaffold, fill context, panel-init, first ingest batch.
---

Run the **new-engagement** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/new-engagement.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing before scaffolding): `$ARGUMENTS`

Expect: client short-code · engagement/tender id · engagement name · destination root ·
**mode** (`research` | `pursuit` | `delivery` | `full`, comma-combinable).

Step 0 of the playbook is picking the mode — do not default to `full` without checking what the
work actually is. Building a block "just in case" leaves empty folders that every later skill
will hunt through.
