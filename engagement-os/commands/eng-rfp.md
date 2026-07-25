---
description: An RFP / tender arrived — run the bid loop: ingest the pack, analyse it into a compliance matrix, go/no-go, close the gaps with cited research, write the response, red-team before submit.
---

Run the **rfp-arrived** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/rfp-arrived.md`

Read that file and follow it exactly, including its stop gates. It owns the chain and every
rule; do not reproduce, summarise, or improvise the steps here — a copied rule rots.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: the path to the tender pack, and the engagement/tender id.
