---
name: eng-render
description: >-
  Use when a set of written markdown sections (plus their figures) must become the delivered
  artefact — a Word/PDF document or a slide deck. Triggers on FORMAT verbs only, such as
  "render this directory as a deck", "turn these MD files into a Word doc", "generate the PPT
  from these sections", "export these sections to docx/pdf", or "what would this build into";
  and on the deck round trip after that, such as "splice these corrected slides back into the
  deck" or "check this deck before I send it". Writing or assembling the CONTENT is
  eng-bid-respond / eng-build-deliverable — this skill never drafts. Works standalone on ANY
  directory of markdown; needs no engagement scaffold, compliance matrix, or prior eng-* step.
---

# Rendering written sections into the delivered artefact

The last step, and **only** the last step: content that is already written and reviewed becomes
the file the client receives. Nothing here writes content, designs a figure, or decides an
argument — if any of that is still open, this is the wrong skill.

**Standalone by design.** Point it at a directory. It does not care how the markdown got there,
which phase produced it, or whether an engagement repo exists around it.

**Dependency (packaging note).** The engines are
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/render_document.py` and, for the deck gate,
`verify_deck.py` — this skill is the facade; both live with the eng-os kernel alongside
`eng_lint.py` and the scaffolder. Installing or pruning skills individually must keep `eng-os`
for this one to run.

## What this owns, and what it hands off

| Step | Owner | Why not here |
|---|---|---|
| discover · order · strip · gate · measure | **this skill** (`render_document.py`) | the only part specific to how we write sections |
| markdown → docx/pdf | `pandoc` + `soffice`, per the **`docx`** skill | a converter is a solved problem |
| figures | **`designing-figures`** | archetype before pixels; already a skill |
| slide deck | **`presentation-builder`** | it owns storyline, action titles, and the editable export |
| copying slides between decks | the **`pptx`** skill | verbatim slide copy + running order is solved there |
| is the assembled package safe to send | **this skill** (`verify_deck.py`) | the one step nothing else owned |

The handoffs are the point. A deck built here would be a worse `presentation-builder`, and a
converter written here would be a worse pandoc.

## Workflow

```
- [ ] 0. Invoke `Skill(engagement-os:eng-propagate-change)`. Stop on any unresolved impact;
        rendering stale approved content only makes the stale state harder to see.
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
- [ ] 4. DOCUMENT: same script, --to docx|pdf|both. Typography: --font/--size are
        enforced through a generated pandoc reference.docx (the docx writer ignores
        pandoc's mainfont/fontsize metadata — that mechanism never worked); if the
        buyer mandates a template, pass it as --reference-doc instead. Generated documents
        default to `--paper a4`; use `--paper letter` only when the recipient requires it.
        A buyer-supplied reference document controls its own paper size. Re-check the
        PAGE COUNT the build prints against the budgets — a word estimate is an estimate.
- [ ] 5. DECK, first build: --to deck-manifest --audience "..." --decision "...", then
        invoke the `presentation-builder` skill with the manifest. Audience and decision
        are recorded IN the manifest so the handoff survives being re-run from the file.
- [ ] 5b. DECK, correcting an issued one: do NOT rebuild it. Write the running order
        down, splice the redrawn slides in via the `pptx` skill, keep every other slide
        untouched → references/deck-assembly.md (in eng-os).
- [ ] 6. Gate the package, then verify the artefact — not the log:
        python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/verify_deck.py <deck.pptx> \
          --expect <slide count you intended>
        Then open the file: every figure present, every internal marking gone.
```

## Profiles are policy, not mechanism

A profile says what "ready to ship" means for this kind of artefact. Pick the one that matches
the recipient; add a new one in the script's `PROFILES` table rather than special-casing.

| Profile | Ships when | Because |
|---|---|---|
| `plain` | always | notes, internal drafts, a working read-through |
| `bid` | every section `reviewed-r2`/`approved`, no `[⚠VERIFY]` in body text | a tender is scored once |
| `deliverable` | every section `reviewed`/`approved`/`issued`, no `[⚠VERIFY]` | it carries our name |

`--force` overrides a policy gate and **reports every gate it overrode as an advisory**, so a
forced build still tells you the status it ignored and how many `[⚠VERIFY]` markers are in the
text. **A missing figure is never overridable** in any profile: pandoc degrades a missing image to
its alt text, so the document builds happily and the figure is simply gone.

The legitimate use of `--force` is measurement, not shipping: pointing it at a single unapproved
section under `--profile bid` is the only way to learn that section's real submission page count
before the review rounds finish — and the page budget is the one constraint that changes what you
write. A `plain` build measures a different document (it keeps the scaffolding).

`[⚠VERIFY]` is matched in every written form, including the explanatory
`[⚠VERIFY — what would close it]` that real sections carry. Matching only the bare literal let
eight markers through onto a rendered tender page.

## What gets stripped

Sections are written to be *checkable*; that scaffolding must not reach a reader — scoring notes
(`>` blocks), the `**Figure source.**` pointer to a figure's editable master, the traceability
line, the review log. A figure *caption* is client-facing text and is NOT stripped, so the
editable-master filenames belong on the `**Figure source.**` line and nowhere else. The strip is mechanical and lives in the
script, because doing it by hand is how internal scaffolding reaches an evaluator.

Stripping happens **only under `bid`/`deliverable`** — the blockquote = scoring-note convention
is part of the section contract, and applied to arbitrary markdown it would silently delete
legitimate quotations. `plain` renders what is there. Under a stripping profile, every stripped
blockquote run is reported on stderr by file and line count — visible, never silent.

`[⚠VERIFY]` is **not** stripped. It is body prose, so removing it would ship the unsupported
claim silently; the gate blocks instead.

## A deck is not a reformat of a document

Prose sized to a page budget does not become slides by pagination — it overflows onto untitled
continuation slides and orphans figure captions. That is why the deck route emits a *manifest*
and hands off: `presentation-builder` re-cuts the argument into one message per slide.

Housekeeping: `presentation-builder` may leave its working artefact (a storyline draft such as
`<name>_readthrough.md`) beside the deck. It is an intermediate, safe to delete; the manifest
and the deck are the contract.

Once a deck exists, corrections are a **splice**, not a rebuild, and the assembled package gets
gated by `verify_deck.py` before it goes anywhere. Both live in eng-os
`references/deck-assembly.md` — including the two defects that are invisible in a build log and
only visible in the package (a flattened picture-per-slide deck; a font neither standard nor
embedded).

## Guardrails

- **Every figure keeps an editable path.** The manifest carries each figure's `.html` source and
  its one-slide editable `.pptx` beside the `.png`, so a reviewer corrects the figure instead of
  describing the correction in prose. The analyse report flags any figure that has only a PNG.
- Never render from sections that are still being argued about. Rendering early makes the format
  the subject and the content an afterthought.
- Re-render rather than editing the output. The markdown and the figure HTML are the masters;
  a hand-edit to the `.docx` is lost on the next build.
- If a reviewer did edit DOCX/PDF/PPTX directly, invoke
  `Skill(engagement-os:eng-propagate-change)` to reconcile that edit into the maintained source
  before rendering; never checkpoint the generated-file edit as authoritative.
