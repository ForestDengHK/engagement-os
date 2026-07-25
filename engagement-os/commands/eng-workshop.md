---
description: A workshop or discovery session just ended — turn held-notes into findings, fold canonical deltas, update the question backlog, log the session.
---

Run the **post-workshop** playbook:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/playbooks/post-workshop.md`

Read that file and follow it exactly, including its stop gates. It owns the chain; do not
reproduce or improvise the steps.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: which session, and the path to the held-notes / transcript.

A finding is a **fact baseline, not a recommendation** — keep observation and interpretation
visibly separate, and tag evidence by how it was obtained.

Draft the held-notes from whatever raw material was supplied; ask only for what's
missing. Do not hand the user a blank template.
