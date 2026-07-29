# Exhibit Spec — fill this BEFORE drawing, get sign-off

> One spec per exhibit. Revising words here is cheap; revising pixels later is not.
> In `presentation-builder` batch mode, fill one of these per visual slide and review them all at once.

```
Action title (the ONE message):   <the sentence the exhibit must make true>
Audience / decision:              <who reads it / what they decide from it>
Archetype:                        <layered | swimlane | capability-grid | maturity-heatmap |
                                   sankey | matrix | network | composition | roadmap | kpi-hero>
                                   (why this one: ____)

Structure (fill the one that matches the archetype):
  Layers / lanes:                 <ordered list>
  Rows (e.g. domains):            <list>           Columns (e.g. lifecycle):  <list>
  Nodes / flows (sankey/network): <nodes + which connects to which, with weights>
  Axes (matrix):                  <x-axis low→high, y-axis low→high>

Per-cell / per-item content:      <what text + which encoding goes in each unit>
Emphasis (the spine / focus):     <the load-bearing node to make dominant>
Encoding:                         <severity or maturity colour scale; size ∝ ?; line semantics>
Cross-cutting band:               <governance / security / personal-data, if any>
Icon strategy:                    <official set (which) | category glyphs (which) | none>
Brand tokens / palette / font:    <which token set>
Legend + source line:            <what the legend explains; the footnote>

Open questions / facts to confirm: <numbers or labels you are unsure of>
```

## Worked example (the GNI current-state landscape)

```
Action title:   A single ageing Oracle 19c warehouse underpins the entire estate;
                demand is shifting to self-service BI faster than governance can follow.
Audience:       GNI data lead + steering committee / decide modernisation priorities & risk.
Archetype:      Layered landscape + cross-cutting band  (warehouse made the visual spine).
Layers:         Sources → Ingestion → Oracle 19c warehouse → Semantic/Consumption → Consumers
Emphasis:       Stage 3 warehouse = spine (single point of failure = the message).
Encoding:       Severity S1/S2/S3 badges + legend; blue dot = data flow.
Cross-cutting:  Governance & ownership / Security & regulatory / Personal data.
Icon strategy:  Category glyphs (Lucide), one teal tint — mixed-vendor estate, no logo zoo.
Brand:          GNI tokens (indigo/blue/teal, Open Sans).
```
Same spec, archetype swapped to `maturity-heatmap` and `sankey`, produced the other two `examples/`.
