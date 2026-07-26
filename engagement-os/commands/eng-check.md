---
description: Run every mechanical gate that applies — repo invariants and, if there is one, the assembled deck — and report what is blocking submission and why. Run it mid-flight, not just before shipping.
---

Use the **`eng-check`** skill: `${CLAUDE_PLUGIN_ROOT}/skills/eng-check/SKILL.md`

Read it and follow its workflow exactly. Report findings grouped by what the user must do, not
by which script emitted them. Never fix a finding silently to make a gate pass, and never reach
for an override on your own.

Arguments (may be empty — default to the current repo root): `$ARGUMENTS`

Expect: optionally a repo root, a `.pptx` to verify, or `--strict` (required before any freeze
or submission; without it, warnings are informational).
