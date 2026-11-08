---
name: presentation-builder
description: Use when turning a body of context, research, notes, or an assessment into a full client-grade slide deck (Deloitte / McKinsey / Microsoft style) where every figure must look mature and professional — not just bullet slides. Use when the goal is "make the whole deck from my context, with beautiful, professional figures", or to upgrade a deck whose diagrams look generic. Prefer this over calling pptx / baoyu-design / ppt-master directly when the deck (PPT/PPTX/presentation/汇报材料) is built from substantial context and figure quality matters — it routes production to those tools. Also use to review a deck the user already has against a client-grade checklist — "review my deck", "what's wrong with these slides", "check my slides against best practice", "帮我看看这个PPT", "这个 deck 哪里不专业" — findings per slide, never added or restored slides. A colleague's or team's deliverable goes to deliverable-review.
---

# Presentation Builder

## Overview

The umbrella workflow for producing a **client-grade deck from context**, where the visuals are as good as the words. It composes three capabilities:

1. **Storyline** — structure the argument (this skill).
2. **Figures** — every figure goes through **`designing-figures`** (spec before pixels, archetype grammar). **REQUIRED SUB-SKILL.**
3. **Production** — assemble + render. The default is a python-pptx build that draws every figure as **native shapes, connectors and tables** from its spec; other paths are in Tool routing.

**This is a thin orchestration wrapper, not a new engine.** It does NOT replace your PPT-production tool. It adds the storyline layer and enforces one invariant: **every figure in the deck is generated through `designing-figures`** (never the lazy default). The `.pptx` bytes are still produced by whatever build you route to in step 5.

**Core principle: storyline before slides; spec before pixels.** Decide the narrative and each figure's spec first; build last. The bottleneck for "Deloitte-looking" output is design thinking, not the rendering tool.

## When to use

- "Here's all my context / research / assessment — make the deck."
- A deck must look like a top-tier consulting/Microsoft deliverable, with real figures not clip-flowcharts.
- Upgrading an existing deck whose content is fine but diagrams look amateur (→ re-do each figure via `designing-figures`).
- **Not** for a single one-off figure (use `designing-figures` directly) or a plain text doc (use a docs skill).

## Workflow

1. **Absorb context & set the throughline.** Read the source material. Write the deck's single governing message and the audience + decision. Pick the spine by content type + audience. **See `references/planning-playbook.md`** (SCQA opening, Pyramid/answer-first, MECE, vertical+horizontal logic, content-type → structure map, audience depth, the storyboard method).
2. **Outline as action titles.** One slide = one message; title = the takeaway sentence, not a topic. The titles read in order must tell the whole story (horizontal logic). Keep groups MECE. **Get the title outline agreed (gate 1) before drafting figure specs or building.** (If no user is available — autonomous run — self-review the outline against the playbook, note open questions, and proceed.)
3. **Classify each slide** → text/table vs **figure**. For every figure slide, draft its spec with **`designing-figures`** (`assets/spec-template.md`): action title → archetype (its grammar table) → structure → encoding → icon strategy. **Review all specs together** in one gate, then build. (Autonomous run: self-review the specs per `designing-figures`' squint-test criteria and proceed.)
4. **Lock one visual system** for the whole deck (brand tokens, type scale, severity/legend) so slides and figures look like one family. Reuse the client's deck tokens if they exist.
5. **Build via the routed path** (below). The default production path: python-pptx, each figure drawn on its slide as native shapes / connectors / native tables from its spec (`destination: deck`), grouped so it moves as one — `designing-figures` `references/render-pipeline.md` §7. The HTML render is the design reference, not the artefact. A picture goes on a slide only for a photograph or a screenshot. Leave fonts unset so the template's theme fonts apply. If the manifest says `figure_policy: native`, that is binding.
6. **QA — squint test every slide** with fresh eyes (a subagent over the rendered images). If no subagent is available, render every slide to PNG (soffice → pdftoppm) and inspect each image yourself against the same squint-test checklist; record the pass per slide in the build notes. One message per slide; nothing cramped; figures pass `designing-figures`'s critique. Fix at the structure layer. REQUIRED checks, each reported with its result:
   - **0 picture shapes on slide layers** unless that figure is a photograph or screenshot — `unzip -p deck.pptx 'ppt/slides/slide*.xml' | grep -c '<p:pic>'`; name the slide of every hit.
   - **Type minimums:** body ≥ 12 pt · table ≥ 10 pt · appendix ≥ 9 pt · titles 20–24 pt.
7. **Export** per the routed path.

## Review mode (a deck the user or a colleague made)

Use when the deck already exists and the user asks for a review, a check or an upgrade. When the output is comments for a colleague or team, start in `deliverable-review`; it ends with this checklist.

1. Read the deck in order — `markitdown <deck.pptx>` (titles, body, notes per slide) — and look at every slide's render (`deck-verify` contact sheet).
2. Before calling it client-ready, walk **`references/review-checklist.md`** and report per slide (yes/no + slide number): 1 action titles · 2 slide numbers · 3 acronyms and codes explained · 4 keys on coded tables · 5 no white text on mid-tone fills · 6 options compared before the recommendation · 7 no cross-references or transcript/tracker refs · 8 one message per slide.
3. Then `deck-verify` and `client-face-gate`.
4. The review is findings, not slide edits. Edit only when the user asks for fixes after reading it.

**Keep the user's slide set.** Never add, restore or reorder slides the user set — no cover, divider, purpose, summary or closing slide, and never one they removed — without asking in one line. Propose it in the review instead.

## Deck-level best practices

| Principle | What it means |
|---|---|
| Action titles | Title = the takeaway; the body proves it. Titles alone tell the story. |
| One message per slide | If a slide has two messages, split it. |
| MECE grouping | Sections and bullets are mutually exclusive, collectively exhaustive. |
| Sandwich structure | Dark title + section + closing slides; light content slides between. |
| Evidence under the claim | Each figure exists to prove its action title — cut anything that doesn't. |
| Consistency | One palette, one type scale, one icon strategy across every slide and figure. |
| Self-contained slides | No slide points to another ("see slide 13", "see the last slide"); no transcript or tracker refs, even on internal decks (2026-10-20/21). |

## Tool routing (production is pluggable — decide in this order)

1. **The user named a tool/path** ("use baoyu", "use my build", "just give me the PNGs") → use exactly that. An explicit instruction always wins.
2. **The project already has a deck build** (pptxgenjs / python-pptx) → reuse it; figures drawn as native shapes in that build.
3. **Otherwise python-pptx native build** into the host template (or the built-in `pptx` skill's python-pptx path). State which backend you picked and why in one line.

Then map the chosen path:

| Situation | Path | Editable? |
|---|---|---|
| **Default:** any client deck | python-pptx into the host template; figures as native shapes / connectors / tables from the spec | **yes — every figure** |
| You already have a deck build (pptxgenjs / python-pptx) | Keep it; draw each figure natively in that build (pptxgenjs `addShape` / `addTable` likewise) | **yes** |
| User asked for an HTML-first deck | `baoyu-design` HTML deck → editable-PPTX export | mostly — masked icons, `::before` and gradients arrive as pictures |
| Audio narration / video / template-replica needed | `ppt-master` (heavier); still spec figures via `designing-figures` first | per its export |
| Figure PNG placed on a slide | — | **no — not a deck route; documents only** |

HTML-first route: author at baoyu's 1920 × 1080 and export with `"slideWidthIn": 13.333` in the gen-pptx config — the deck comes out 13.333 × 7.5 in with px = pt × 2, so the 24 px text floor is the 12 pt body minimum. Without it the slide is 20 in wide and every size is off by 1.5×. Web fonts the slides use are embedded automatically; report the printed `embeddedFonts` and any `font_not_embedded` flag.

## Common mistakes

- Building slides before the action-title outline is agreed → rework. Outline first.
- Beautiful template, default diagrams → the diagrams betray it. Every figure goes through `designing-figures`.
- Different colours/fonts per slide → looks assembled, not authored. Lock one system (step 4).
- Generating diagrams as AI images → garbled labels/icons. Figures = real assets + structure you lay out.
- Pasting a figure PNG onto a slide → nobody can correct a label in PowerPoint. On a slide the figure is native shapes.
- Re-reviewing the user's deck against the playbook and adding slides (Client 2026-10-13: purpose slide + cover, restoring a summary he had cut on 7 Oct) → "we keep cover page but remove slide 2". The user's structure wins; propose, don't add.
