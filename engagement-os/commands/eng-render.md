---
description: Point at a directory of written markdown sections and turn it into the delivered artefact — a Word/PDF document, or a slide deck via presentation-builder. Standalone; needs no engagement scaffold.
---

Use the **`eng-render`** skill: `${CLAUDE_PLUGIN_ROOT}/skills/eng-render/SKILL.md`

Read it and follow its workflow. It owns discover/order/strip/gate/measure and hands the rest
off — `docx` for a document, `presentation-builder` for a deck, `designing-figures` for figures.
Do not build a deck or a converter inside this command.

Arguments (may be empty — ask for what's missing): `$ARGUMENTS`

Expect: the **directory** of section markdown. Optionally the output the recipient requires
(document or deck), and the profile (`plain` / `bid` / `deliverable`).

**Analyse before rendering, always** — run the script with `--analyse` first and report what it
found back to the user, including any figure that exists only as a PNG with no editable source.
If the profile gates block, say what is blocking and let the user decide; do not reach for
`--force` on your own.

If the user asks for slides, emit `--to deck-manifest` and invoke `presentation-builder` with it,
telling it the audience and the decision the deck must produce. A deck is a re-cut of the
argument, not a pagination of the document.
