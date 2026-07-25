# Assembling and verifying a deck

A deck is rarely built once. It is built, reviewed, and then *partially* corrected — a handful
of slides get redrawn while the rest stay exactly as issued. This file covers that round trip
and the gate at the end of it. It does not cover storyline (`presentation-builder`), figures
(`designing-figures`), or the editable-deck rule and versioning discipline
([deliverable-build.md](deliverable-build.md) owns both).

## Contents
- Who owns which step
- The round trip
- Splice, don't rebuild
- The gate: what verify_deck checks, and why only these
- Guardrails

## Who owns which step

| Step | Owner | Why not here |
|---|---|---|
| what the deck argues, one message per slide | `presentation-builder` | it owns storyline and action titles |
| how a figure looks, and its editable export | `designing-figures` | archetype before pixels |
| copying / reordering / deleting slides across packages | the **`pptx`** skill | `add_slide.py` copies a slide verbatim; `<p:sldIdLst>` is the running order; `clean.py` finishes. Solved, and its OOXML validator catches the package-level defects |
| sections → the manifest that starts a deck | `eng-render` | the only part specific to how we write sections |
| **is the assembled file safe to send** | **`verify_deck.py`** (this file) | the one step nothing else owned |

Every one-off `merge_v22.py` / `assemble_v34.py` in an engagement repo is a re-implementation of
row 3. Write the running order down, hand the copying to `pptx`, and keep the judgement here.

## The round trip

```
       ┌──────────────── issued deck vX.Y ────────────────┐
       │                                                  │
   review finds N slides wrong                        the rest are correct
       │                                                  │  and must not move
   redraw those N (designing-figures →                    │
   one editable .pptx per slide)                          │
       └──────────► splice them back in ◄─────────────────┘
                            │
                    verify_deck.py --expect <count>
                            │
                    vX.(Y+1) · DELIVERABLES.md · archive vX.Y
```

The failure this prevents is not a bad deck — it is a deck that never gets assembled. Corrected
slides sit beside the deck as loose fragments, the issued version stays live, and the correction
silently expires. **A redraw is not done until it is spliced, verified, and indexed.**

## Splice, don't rebuild

Rebuilding the whole deck to change a quarter of it re-opens every slide nobody asked about, and
each rebuild is where untracked drift enters.

1. **Write the running order down first** — an explicit list of `(source, slide)` pairs, one row
   per output slide, before any copying. It is the artefact that makes the splice reviewable and
   re-runnable; a chain of ad-hoc copy calls is neither.
2. Copy in that order via the `pptx` skill. Structural work (add / delete / reorder) finishes
   before any content edit — a slide copied after editing clones the edit.
3. Slides not in the change list are copied untouched. Not re-exported, not re-styled.
4. `--expect <count>` on the verify run is the arithmetic check on the splice: the count you
   intended, stated up front, not read off the result.

## The gate: what verify_deck checks, and why only these

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/verify_deck.py deck.pptx --expect 45
```

Two of its checks exist because both failures have actually shipped, and neither is visible in a
build log — only in the package:

- **`flattened-slide`** — a full-bleed image with no text on it. Renders perfectly for whoever
  built it; arrives as a dead sheet for the reviewer, who cannot select, correct or search a
  word of it. An error on a client deck. `--review-copy` downgrades it for an internal
  read-through artefact, which is the only legitimate use of a picture-per-slide deck.
- **`font-not-embedded`** — text set in a font that is neither standard-Office nor carried in
  the package. It substitutes on the recipient's machine and the substitute is a different
  width, so labels overflow their boxes on a reviewer's PowerPoint while looking correct on
  yours. A warning, because the honest fix is sometimes "install the font on that machine"
  rather than embed — but it must be a decision, not a discovery.

Plus the mechanical ones a splice gets wrong: `slide-count`, `broken-media-ref` (a figure
whose image did not come across — PowerPoint draws an empty box), `empty-slide`, and
`no-text-on-slide`.

**What it deliberately does not check.** Text overflow within a shape cannot be decided from the
XML — it needs rendered pixels, which `designing-figures`' render-verification pass already owns.
A check that guesses would be worse than no check, because it would be trusted. Schema validity
belongs to the `pptx` skill's validator; run that too when a package looks structurally odd.

Exit codes: `0` clean · `1` findings · `2` unreadable file. Fixtures for every check live in
`tests/test_verify_deck.py`; run it after editing a rule.

## Guardrails

- **Verify the artefact you are about to send, not the one you built.** Re-run the gate on the
  final file after any hand-edit, re-save, or export-to-PDF round trip.
- **A clean gate is not a review.** It proves the package is sound, not that the deck is right —
  `panel-review` is still the shipping gate.
- **Never hand-edit the assembled deck** to fix a slide. The slide's HTML/figure source is the
  master; edit there and re-splice, or the next assembly silently reverts the fix.
