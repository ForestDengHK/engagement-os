---
description: An RFP / tender arrived — run the bid loop: ingest the pack, analyse it into a compliance matrix, go/no-go, close the gaps with cited research, write the response, red-team before submit.
---

Run the **rfp-arrived** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/rfp-arrived.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: the path to the tender pack, and the engagement/tender id.

Hard gates: **stop at the go/no-go** for a human decision before any writing effort; stop before
submission if any mandatory requirement is unmet or a format rule is breached. Nothing from
`_sources/engagement/` may be cited in a bid.
