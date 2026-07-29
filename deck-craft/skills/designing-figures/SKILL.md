---
name: designing-figures
description: Use when creating ANY figure for a slide or report from existing context — a diagram, chart, workflow, architecture, data landscape, process flow, matrix, or data chart (bar/line/pie/KPI) — especially when the default comes out generic, cramped, one-row-of-boxes, or "ugly", or when a figure must look client-grade (Deloitte / McKinsey / Microsoft style). Use BEFORE drawing. Covers every figure in a deck, not just architecture.
---

# Designing Figures

## Overview

**The bottleneck in a good figure is information design, not the rendering tool.** Weak figures happen because the agent jumps straight to "boxes in a row" (or a default bar chart) without first deciding *the one message* and *the visual structure that carries it*. Experts decide structure first; drawing is just execution.

**Core rule: spec before pixels.** Produce a one-line message + spec, get it agreed, *then* render. Quality is decided at the spec layer (cheap to revise), not the pixel layer (slow, expensive).

This is the rendering-tool-agnostic *thinking + system* for figures. It pairs with `presentation-builder`, which calls it for **every** visual in a deck.

## When to use

- Any "draw / diagram / chart / visualize / map" request from context — architecture, workflow, data landscape, process, relationships, **and ordinary data charts** (bar/line/pie/KPI).
- A slide/report figure must look professional, not a default flowchart or a raw Excel chart.
- You have rich context and the naive figure would be a flat row of boxes or an unstyled chart.
- **Not** for a trivial 2–3 box sketch where structure is obvious — draw that directly.

> **Obvious chart type?** (a single clear bar/line/pie) — you may **skip archetype selection (step 2)**, but still do the message (step 1) and **always apply the visual system (step 4)**: brand tokens, restraint, hierarchy, one accent, legend. An ugly bar chart is ugly because it skipped the system, not the chart type.

## Workflow (do NOT skip to step 6)

1. **Extract the message.** Write the *action title* — the one sentence the figure must make true. Name the audience and the decision they make from it.
2. **Pick the archetype** from the grammar — 80% of whether it looks expert. See `references/archetype-grammar.md`. Match message → figure type; don't default to a flow.
3. **Structure content MECE** into that archetype: the exact rows / columns / layers / lanes / series and what's in each.
4. **Lock the visual system**: brand tokens, grid, palette, type, icon strategy, legend, line semantics. See `references/visual-system.md`. (Applies to charts too.)
5. **Write the spec and get sign-off.** Fill `assets/spec-template.md`. Iterate *on the spec*, not pixels. (In `presentation-builder` batch mode this is one combined review of all specs.) If no user is available to sign off (autonomous run), self-review the spec against the squint-test criteria, note open questions in the output, and proceed.
6. **Render** on a strict grid with real assets. See `references/render-pipeline.md`.
7. **Critique — the squint test** (below). Iterate at the *structure* layer.
8. **Output** per `references/render-pipeline.md` §5.

## Output & editing — read this

- The figure's **editable master is the HTML source**, not the image. You never edit the PNG (same as you never edit a draw.io `.png` — you edit the `.drawio`). Change text/numbers/colour in the HTML, re-render.
- **Default output is a PNG** (headless-Chrome screenshot). It drops into ANY deck/report tool — a pptxgenjs/python-pptx build, the built-in `pptx` skill, your own deck script, Google Slides. **No dependency on baoyu.**
- **Need to edit inside PowerPoint** (native shapes/text)? Use the optional `baoyu-design` HTML→editable-pptx export. Caveat: masked icons / CSS `::before` don't convert — for icon-heavy figures, place the PNG instead.
- Full decision table in `references/render-pipeline.md` §5.

## The squint test (mandatory critique)

Squint at the render. In 3 seconds:
- Does ONE structure/message read? If not, the archetype or hierarchy is wrong — fix structure, not colours.
- Does the eye land on what matters (the spine, the gap, the concentration, the one bar)? Encode importance with size / colour / position.
- Strict grid, real whitespace? Uneven gaps and cramped 10px text are the amateur tells.
- Cut anything that doesn't serve the action title.

## Common mistakes

| Mistake | Fix |
|---|---|
| Straight to "one row of boxes" / a default chart | Pick archetype by message first (step 2) |
| Everything one visual weight | Encode hierarchy: spine dominant, rest muted |
| A zoo of half-available vendor logos | Mixed-vendor → category glyphs + text. Official icons ONLY when a complete set exists (AWS/Azure); never AI-generate brand/service icons |
| Cramped tiny text, hairline borders | Strict grid, generous padding, brand type scale |
| Drawing before agreeing structure | Spec first (step 5) |
| "It's just a bar chart, skip the skill" | Skip archetype selection, NOT the visual system (step 4) |

## Worked examples

Same content, three archetypes (the whole point) — in `examples/`:
- `example_layered_landscape.html` — layered value-chain + a "spine" node (overview).
- `example_maturity_heatmap.html` — same data, colour-coded by maturity (where the gaps are).
- `example_flow_sankey.html` — SVG Sankey, ribbon width ∝ volume (where load concentrates).
