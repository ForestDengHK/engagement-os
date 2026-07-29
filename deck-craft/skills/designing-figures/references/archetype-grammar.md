# Archetype Grammar — message → diagram type

Picking the archetype is the single biggest lever on whether an exhibit reads as expert.
**Find the row whose "message" matches your action title; build that archetype. Do not default to a flow.**

| The message is about… | Archetype | Layout recipe | Use for |
|---|---|---|---|
| **Structure / a stack** | Layered architecture | Horizontal or vertical bands; one cross-cutting band (security/governance) along an edge; consistent boxes per layer | Tech stacks, data platforms, app tiers |
| **A process / request path** | Swimlane / value chain | Left→right stages; numbered steps; arrows; optional actor lanes | End-to-end workflows, request flows |
| **Coverage / a landscape** | Capability map / 2-D grid | Rows = domains, cols = lifecycle stages; cells = systems; optional cross-cutting band | "What exists" across an estate — **data landscapes** |
| **Health / where the gaps are** | Maturity heatmap | Same grid/landscape, each cell tinted healthy / constrained / gap; tally + legend | Current-state assessment, gap analysis |
| **Volume / where load concentrates** | Sankey / flow-weighted | Nodes sized by volume; ribbon width ∝ flow; show bypasses | Traffic concentration, data movement, spend |
| **Positioning / trade-off** | 2×2 matrix | Two axes; plot items in quadrants; label axes; ≤8 items | Prioritisation, build-vs-buy, value vs readiness |
| **Relationships / dependencies** | Network / dependency graph | Nodes + typed edges; cluster by group; legend for edge meaning | Integrations, lineage, org/system maps |
| **Composition / share** | Stacked bar / treemap / waterfall | Proportional segments; one accent for the focus segment | Cost breakdown, portfolio mix, bridge |
| **Over time / sequencing** | Roadmap / Gantt / timeline | Linear time axis; bars ∝ duration aligned to axis; phase gridlines | Implementation plans, waves |
| **One number that matters** | KPI hero / callout | One huge figure + tiny label + one supporting stat | Executive takeaway, section opener |

## Decision shortcuts

- "Show me the architecture" → **Layered** (almost never a flat flow).
- "Data landscape / estate" → **Capability map / 2-D grid**, or **Maturity heatmap** if the point is gaps.
- "How does X flow / where does it go" → **Swimlane** (steps) or **Sankey** (if volume/concentration is the point).
- "Which should we pick / prioritise" → **2×2 matrix**.
- "How do these connect" → **Network**.

## The same content, three archetypes

One estate, three messages, three exhibits (see `examples/`):
- *"Everything runs through one warehouse"* → **Layered** with that warehouse as the visual **spine**.
- *"Where are the gaps"* → **Maturity heatmap**.
- *"Load concentrates on Maximo→warehouse→SharePoint"* → **Sankey**.

If swapping the archetype changes the story, you chose the right one. If any archetype would "work", you haven't found the message yet (go back to step 1).

## Cross-cutting bands

Governance / security / compliance / personal-data usually belong as a **single band along one edge** spanning all columns — not as another column. They apply *across* the structure; encode that spatially.

**Exception — governance as an assessed stage, not an applied control.** If "Govern" is one of the things being *rated per item* (e.g. a domain × lifecycle maturity grid where each domain has a Govern score), it is a legitimate **column/stage**, not an edge band. Rule of thumb: applied *across* everything → edge band; *assessed per row* → column.

## Encoding importance (every archetype)

- **Spine**: the load-bearing node (the one warehouse, the dominant system) gets heavier treatment — filled brand colour, larger, centred — so the eye lands there.
- **Severity / maturity**: a fixed colour scale (e.g. Critical→Open or healthy/constrained/gap) + a legend. Reserve red/green for real negative/positive semantics.
- **Volume**: size (bar height, ribbon width, node area) ∝ the quantity. Never draw equal boxes for unequal things.
