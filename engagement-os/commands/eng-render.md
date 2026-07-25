---
description: Point at a directory of written markdown sections and turn it into the delivered artefact — a Word/PDF document, or a slide deck via presentation-builder. Standalone; needs no engagement scaffold.
---

Use the **`eng-render`** skill: `${CLAUDE_PLUGIN_ROOT}/skills/eng-render/SKILL.md`

Read it and follow its workflow exactly — analyse first, always; its gates, profiles and
handoffs are defined there and only there. Do not build a deck or a converter inside this
command, and do not reach for `--force` on your own.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: the **directory** of section markdown. Optionally the output the recipient requires
(document or deck), and the profile (`plain` / `bid` / `deliverable`).
