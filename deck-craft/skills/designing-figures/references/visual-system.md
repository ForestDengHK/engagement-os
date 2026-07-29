# Visual System — lock this before drawing

A "designed" look comes from a consistent system applied with restraint, not from decoration.

## 1. Brand tokens

Pull the client/brand palette + fonts and use them as CSS variables. Never invent colours.
Start from `assets/brand-tokens.css` (ships a GNI set + a generic corporate set) and swap values.

If you have a brand deck/build script, lift tokens from it (e.g. GNI: ink `#06038D`, blue `#0099FF`, teal `#007A82`, green `#84BD00`, severity scale, Open Sans). A diagram that uses the deck's exact tokens looks like it belongs in the deck.

## 2. Restraint

- **2–3 colours + one accent.** One colour dominates (~60%), 1–2 support, one sharp accent for the focus.
- Reserve **red/green** for real negative/positive semantics (severity, maturity), not decoration.
- Generous whitespace. ≥24px gaps, real padding inside cards. Cramped = amateur.

## 3. Grid & hierarchy

- Lay everything on a **strict grid** (CSS grid `repeat(N,1fr)` + consistent `gap`). Equal columns, aligned edges.
- **Hierarchy by size / weight / colour**, not by 10px-vs-11px. Bold ink for the load-bearing label; muted for detail.
- Make the spine/focus node visually dominant (filled brand colour, larger).

## 4. Type scale (1920×1080 canvas)

| Role | px |
|---|---|
| Section title | 44–56 |
| Kicker / eyebrow | 18–22 (uppercase, letter-spaced, accent colour) |
| Stage / card heading | 19–26 bold |
| Body / detail | 13–16 |
| Legend / footnote | 12–14 muted |

Never below ~13px on a slide-scale canvas. Use the brand font with a system fallback; `@import` Google Fonts is fine in the render step.

## 5. Icon strategy (decision)

| Situation | Use | Source |
|---|---|---|
| Cloud architecture (AWS / Azure / GCP) | **Official service icons** | AWS: `awslabs/aws-icons-for-plantuml` dist; Azure/GCP: official icon sets. Real, recognizable, trademark-safe |
| Mixed-vendor estate (Oracle/SAP/Power BI/…) | **Consistent category glyphs + text labels** | Lucide / Tabler (MIT). One set, recoloured to one brand tint. Names go as text |
| Decorative / illustration / background | AI-generated raster | image-gen backend — **never** for service/brand icons |

**Why not vendor logos for mixed estates:** big-vendor logos are often unavailable (simple-icons drops Oracle/PowerBI/SharePoint/IBM for trademark) → you get an inconsistent half-set, which looks worse than none. Category glyphs are cohesive and always available.

**Recolouring stroke/mono SVGs** (Lucide/simple-icons) via CSS mask:
```css
.ic{ width:24px;height:24px; background: var(--ink);
     -webkit-mask: url(icons/lucide-database.svg) center/contain no-repeat;
     mask: url(icons/lucide-database.svg) center/contain no-repeat; }
```
(Mask uses the icon's alpha; `background` becomes its colour. Works for any single-colour SVG; renders in headless Chrome PNG. Note: masks don't survive HTML→editable-PPTX, so for pptx output render the exhibit to PNG and place the PNG — see render-pipeline.)

## 6. Line / connector semantics

Pick a fixed meaning and put it in the legend:
- Solid = synchronous / primary; dashed = async / batch / secondary.
- Colour = data flow vs control flow vs bypass.
- Arrowhead direction always consistent (left→right reading).
- Weight ∝ volume when volume is the message (Sankey).

## 7. Legend + action title are mandatory furniture

Every exhibit carries: an **action-title** (the message, as a heading or a "KEY MESSAGE" band), a **legend** for any colour/line encoding, and a small **source/footnote** line. These are what make it read as a deliverable rather than a sketch.
