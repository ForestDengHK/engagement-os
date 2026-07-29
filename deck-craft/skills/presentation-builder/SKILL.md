---
name: presentation-builder
description: Use when turning a body of context, research, notes, or an assessment into a full client-grade slide deck (Deloitte / McKinsey / Microsoft style) where every figure must look mature and professional — not just bullet slides. Use when the goal is "make the whole deck from my context, with beautiful, professional figures", or to upgrade a deck whose diagrams look generic. Prefer this over calling pptx / baoyu-design / ppt-master directly when the deck (PPT/PPTX/presentation/汇报材料) is built from substantial context and figure quality matters — it routes production to those tools.
---

# Presentation Builder

## Overview

The umbrella workflow for producing a **client-grade deck from context**, where the visuals are as good as the words. It composes three capabilities:

1. **Storyline** — structure the argument (this skill).
2. **Figures** — every figure goes through **`designing-figures`** (spec before pixels, archetype grammar). **REQUIRED SUB-SKILL.**
3. **Production** — assemble + render. **No single tool is required**; pick the path that fits (see Tool routing): your own pptxgenjs/python-pptx build consuming figure **PNGs**, the built-in `pptx` skill, or `baoyu-design` for an HTML deck → editable PPTX.

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
5. **Build via the routed path** (below). Render each figure per `designing-figures` `references/render-pipeline.md` and place it (PNG into a build; or native HTML if using a baoyu deck).
6. **QA — squint test every slide** with fresh eyes (a subagent over the rendered images). One message per slide; nothing cramped; figures pass `designing-figures`'s critique. Fix at the structure layer.
7. **Export** per the routed path.

## Deck-level best practices

| Principle | What it means |
|---|---|
| Action titles | Title = the takeaway; the body proves it. Titles alone tell the story. |
| One message per slide | If a slide has two messages, split it. |
| MECE grouping | Sections and bullets are mutually exclusive, collectively exhaustive. |
| Sandwich structure | Dark title + section + closing slides; light content slides between. |
| Evidence under the claim | Each figure exists to prove its action title — cut anything that doesn't. |
| Consistency | One palette, one type scale, one icon strategy across every slide and figure. |

## Tool routing (production is pluggable — decide in this order)

1. **The user named a tool/path** ("use baoyu", "use my build", "just give me the PNGs") → use exactly that. An explicit instruction always wins.
2. **The project already has a deck build** (pptxgenjs / python-pptx) → reuse it; figures as PNG.
3. **Otherwise default to `baoyu-design`** (HTML deck → editable-PPTX export) — the preferred production backend.
4. **Fall back to the built-in `pptx` skill** if baoyu-design is unavailable or the deck is plain text/tables where an HTML stage adds nothing. State which backend you picked and why in one line.

Then map the chosen path:

| Situation | Path |
|---|---|
| Default: deck from scratch, figure quality matters | `baoyu-design` HTML deck → editable-PPTX export (PNG-place masked-icon figures) |
| You already have a deck build (pptxgenjs / python-pptx) | Keep it. Drop figure **PNGs** from `designing-figures` into its image folder. Edit a figure = edit its HTML source, re-render, rebuild. **No baoyu needed.** |
| baoyu-design unavailable, or plain text/table deck | Built-in `pptx` skill; place figure PNGs |
| Audio narration / video / template-replica needed | `ppt-master` (heavier); still spec figures via `designing-figures` first |

## Common mistakes

- Building slides before the action-title outline is agreed → rework. Outline first.
- Beautiful template, default diagrams → the diagrams betray it. Every figure goes through `designing-figures`.
- Different colours/fonts per slide → looks assembled, not authored. Lock one system (step 4).
- Generating diagrams as AI images → garbled labels/icons. Figures = real assets + structure you lay out.
- Treating baoyu as the only option → it's the *default*, not a requirement. Production is pluggable; PNGs work with any deck tool.
