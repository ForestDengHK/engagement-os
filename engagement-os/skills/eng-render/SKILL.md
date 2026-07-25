---
name: eng-render
description: Use when a set of written markdown sections (plus their figures) must become the delivered artefact — a Word/PDF document or a slide deck. Triggers on "render this directory as a deck", "turn these MD files into a Word doc", "generate the PPT from these sections", "make the submission file", "what would this build into". Works standalone on ANY directory of markdown; needs no engagement scaffold, no compliance matrix, no prior eng-* step.
---

# Rendering written sections into the delivered artefact

The last step, and **only** the last step: content that is already written and reviewed becomes
the file the client receives. Nothing here writes content, designs a figure, or decides an
argument — if any of that is still open, this is the wrong skill.

**Standalone by design.** Point it at a directory. It does not care how the markdown got there,
which phase produced it, or whether an engagement repo exists around it.

## What this owns, and what it hands off

| Step | Owner | Why not here |
|---|---|---|
| discover · order · strip · gate · measure | **this skill** (`render_document.py`) | the only part specific to how we write sections |
| markdown → docx/pdf | `pandoc` + `soffice`, per the **`docx`** skill | a converter is a solved problem |
| figures | **`designing-figures`** | archetype before pixels; already a skill |
| slide deck | **`presentation-builder`** | it owns storyline, action titles, and the editable export |

The handoffs are the point. A deck built here would be a worse `presentation-builder`, and a
converter written here would be a worse pandoc.

## Workflow

```
- [ ] 1. ANALYSE first — always. Never render blind:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/render_document.py \
          --sections <dir> --analyse --profile <plain|bid|deliverable>
        Reports every section's status, word count, page budget, and figure state
        (e = editable source present · p = png only · ! = MISSING), then says
        whether it would build.
- [ ] 2. Read the report back to the user before building. A blocker is information,
        not an obstacle to route around.
- [ ] 3. Pick the route from what the *recipient* requires — not from what is easiest:
          a document (page limits, a mandated template, a submission portal)  → step 4
          a presentation (a meeting, a defence, a steering committee)          → step 5
- [ ] 4. DOCUMENT: same script, --to docx|pdf|both. Re-check the PAGE COUNT it prints
        against the budgets — a word estimate is an estimate.
- [ ] 5. DECK: --to deck-manifest, then invoke the `presentation-builder` skill with the
        manifest. Tell it the audience and the decision the deck must produce.
- [ ] 6. Verify the artefact, not the log. Open the file. Confirm every figure is
        present and every internal marking is gone.
```

## Profiles are policy, not mechanism

A profile says what "ready to ship" means for this kind of artefact. Pick the one that matches
the recipient; add a new one in the script's `PROFILES` table rather than special-casing.

| Profile | Ships when | Because |
|---|---|---|
| `plain` | always | notes, internal drafts, a working read-through |
| `bid` | every section `reviewed-r2`/`approved`, no `[⚠VERIFY]` in body text | a tender is scored once |
| `deliverable` | every section `reviewed`/`approved`/`issued`, no `[⚠VERIFY]` | it carries our name |

`--force` overrides a policy gate. **A missing figure is never overridable** in any profile:
pandoc degrades a missing image to its alt text, so the document builds happily and the figure
is simply gone.

## What gets stripped

Sections are written to be *checkable*; that scaffolding must not reach a reader — scoring notes
(`>` blocks), the traceability line, the review log. The strip is mechanical and lives in the
script, because doing it by hand is how internal scaffolding reaches an evaluator.

`[⚠VERIFY]` is **not** stripped. It is body prose, so removing it would ship the unsupported
claim silently; the gate blocks instead.

## A deck is not a reformat of a document

Prose sized to a page budget does not become slides by pagination — it overflows onto untitled
continuation slides and orphans figure captions. That is why the deck route emits a *manifest*
and hands off: `presentation-builder` re-cuts the argument into one message per slide.

## Guardrails

- **Every figure keeps an editable path.** The manifest carries each figure's `.html` source and
  its one-slide editable `.pptx` beside the `.png`, so a reviewer corrects the figure instead of
  describing the correction in prose. The analyse report flags any figure that has only a PNG.
- Never render from sections that are still being argued about. Rendering early makes the format
  the subject and the content an afterthought.
- Re-render rather than editing the output. The markdown and the figure HTML are the masters;
  a hand-edit to the `.docx` is lost on the next build.
