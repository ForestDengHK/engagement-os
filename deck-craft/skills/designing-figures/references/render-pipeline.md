# Render Pipeline — route by the spec's `destination`

| `destination` | Artefact | Route |
|---|---|---|
| `document` (Word / PDF / web) | PNG rendered from the HTML master | §1–§3 |
| `deck` | **native PowerPoint shapes, connectors and tables** drawn from the spec; the HTML is the design reference, not the artefact | §7 |

A raster image goes on a slide only when the content IS a raster — a photograph or a screenshot.

For documents, render exhibits as **HTML/CSS** (best grid + real icons + browser preview), then capture to PNG.

## 1. Canvas conventions

- One self-contained `.html` per exhibit. Canvas **1920×1080** (16:9, matches a slide). `body{width:1920px;height:1080px}`.
- `@import` the brand font (Google Fonts) at the top; system fallback in the stack.
- Tokens as `:root` CSS variables (copy `assets/brand-tokens.css`).
- Layout with **CSS grid / flex + `gap`** — never absolute-position a grid by hand. Reserve absolute positioning for diagram overlays (connectors, callouts).
- Standard furniture: left brand bar, kicker, action title / key-message band, the exhibit, legend + source footer (see the `examples/`).
- Icons via CSS mask (see `visual-system.md` §5); icon files in an `icons/` folder beside the HTML.
- For Sankey/flow: use an inline `<svg>` for ribbons (cubic-bezier bands), HTML labels on top. See `examples/example_flow_sankey.html`.

## 2. Render to PNG (headless Chrome)

Serve the folder, screenshot at 1:1. PNG is the asset for `destination: document`; for `destination: deck` the exhibit is drawn natively (§7) and no PNG is placed.

```bash
cd <exhibit-folder>
(python3 -m http.server 4321 >/tmp/ea.log 2>&1 &) ; sleep 1
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # or `which google-chrome chromium`
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1920,1080 --default-background-color=FFFFFFFF \
  --screenshot=exhibit.png "http://localhost:4321/exhibit.html"
pkill -f "http.server 4321"
```
Use `--force-device-scale-factor=2` for a 2× (retina) asset.
Rendering several exhibits in parallel? Give each its own port (any free port works) so the `pkill` doesn't kill a sibling render.

## 3. Verify (always)

Open the PNG and run the **squint test** (SKILL.md). For detail, crop regions with PIL and inspect:
```bash
python3 -c "from PIL import Image; Image.open('exhibit.png').crop((40,150,1160,760)).save('crop.png')"
```
First render is rarely right — check overflow, overlap, icon rendering, alignment. Fix at the structure layer, re-render.

**Two traps that yield a stale or broken PNG while everything looks fine:**
- **`timeout` is not on macOS.** A render wrapped in it never runs, and the *previous* PNG is still on disk — verification then passes against a stale image. If a re-render is byte-identical after a real CSS change, suspect the harness before the browser.
- **Never pin the footer with `margin-top:auto`.** On a fixed 1080px canvas the surrounding column flex collapses that row to a few pixels — legend and source line silently vanish from the render while the browser preview looks correct. Pin the footer with `position:absolute` and an explicit `top`, inside a `position:relative` wrapper.

## 4. Optional — export to EDITABLE pptx (baoyu)

When the deliverable must be an editable PowerPoint (not a flat PNG), wrap slides in baoyu's `deck-stage` and export with its `gen-pptx` CLI. One-time setup + invocation:
```bash
SK=~/.claude/skills/baoyu-design
# one-time: cd $SK/agents/gen-pptx && npm install && npx playwright install chromium && npm run build
# config: {"width":1920,"height":1080,"slideWidthIn":13.333,"slides":[{"showJs":"document.querySelector('deck-stage').goTo(0)","selector":"deck-stage > [data-deck-active]"}],"resetTransformSelector":"deck-stage","filename":"exhibit"}
node $SK/agents/gen-pptx/dist/cli.mjs --url <servedDeckUrl> --config <json> --out <dir>
```
**Conversion caveats:** CSS `::before` / `::after` and `mask`-recoloured icons do NOT survive the editable export — draw dots, bullets and markers as **real elements** (`<i class="dot">`) or they vanish from the PPTX while looking fine in the PNG. Text metrics differ from the browser: a label that exactly fits its HTML box can lose its last characters as a PowerPoint shape (found for real: "CARRIES THE DECISION" → "CARRIES THE DECISIO") — leave headroom or shorten the label. CSS gradients become a picture, not a shape (fine for a brand bar, not for content). For exhibits that rely on masked icons: when `destination: document`, prefer **PNG placement** (render §2) over editable conversion; when `destination: deck`, draw the exhibit natively (§7) and place no PNG. Plain shapes, text, real `<img>`, and SVG ribbons convert fine.

**Verify the export, not just the exit code.** Round-trip the PPTX back to an image and compare it with the PNG, then confirm it is genuinely editable rather than a flattened page:
```bash
soffice --headless --convert-to pdf exhibit.pptx --outdir /tmp/v && pdftoppm -png -r 100 /tmp/v/exhibit.pdf /tmp/v/rt
python3 -c "from pptx import Presentation; s=Presentation('exhibit.pptx').slides[0]; \
print(len(s.shapes),'shapes;',sum(1 for x in s.shapes if x.has_text_frame and x.text_frame.text.strip()),'with text')"
```
A one-slide export with 1–2 shapes is a screenshot in a wrapper; a real exhibit comes out as dozens of native shapes carrying editable text.

## 5. Which output when

| Need | Output |
|---|---|
| Figure on a slide (any deck build) | **Native pptx** (§7) — python-pptx shapes from the spec, grouped. **Default for decks.** |
| Figure inside a document (Word / PDF / Markdown) | **PNG** (§2) — drop into the build's image folder |
| A whole HTML deck that must become an editable PowerPoint | baoyu editable export (§4) |
| Quick review with the user | PNG (§2) or serve the HTML and share the URL |

## 6. Editing model — the HTML is the master, never the PNG

The PNG/PPTX is an **output**, not the editable source — exactly like a draw.io `.png` is an export of a `.drawio`. To change a figure:

1. **Edit the HTML source** (labels, numbers, colour are plain readable text — easier to edit than draw.io XML).
2. **Re-render** (§2) → fresh PNG (`destination: document`; place it in the document). For `destination: deck` no PNG is placed — re-run the §7 build instead.

Keep the figure HTML in the repo beside the deck/diagram sources (e.g. next to existing `.drawio` files) so it is version-controlled and re-renderable.

**Two editing modes for the consumer:**
- **Document figures:** change the HTML and re-render the PNG.
- **Deck figures:** change the spec (and the HTML reference if you keep one) and re-run the §7 build script — the slide is native, so a reviewer can also correct a label in PowerPoint directly.

## 7. Destination: deck → native pptx (python-pptx)

The figure is built **on the slide** from its spec: every box, chevron, lane, matrix dot and connector is a PowerPoint shape; every table is a native table (`shapes.add_table`). The whole figure sits in **one group shape** so it moves and resizes as one.

| Spec element | python-pptx |
|---|---|
| box / node / card | `add_shape(MSO_SHAPE.ROUNDED_RECTANGLE …)` with its label in the shape's own text frame |
| process step | `MSO_SHAPE.CHEVRON` / `PENTAGON` |
| swimlane / layer band | full-width `RECTANGLE` + a header `RECTANGLE` |
| matrix dot / severity marker | `MSO_SHAPE.OVAL`, fill from the encoding |
| flow / dependency | `add_connector(MSO_CONNECTOR.ELBOW …)` glued with `begin_connect` / `end_connect` |
| grid of values | `add_table` — never boxes faking a table |
| icon | an editable shape or SVG; a raster icon only if no vector exists |

Rules: leave `font.name` unset so the template's theme fonts apply; sizes — body ≥ 12 pt, table ≥ 10 pt, appendix ≥ 9 pt, titles 20–24 pt; build into the host template (`Presentation("template.pptx")`) so the deck's chrome is kept.

Worked example — a 3-lane swimlane:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from pptx.enum.dml import MSO_LINE
from pptx.enum.text import PP_ALIGN

LANES = ["Client", "Delivery team", "Platform"]          # from the spec: Layers / lanes
STEPS = [(0, 0, "Raise request"), (1, 1, "Triage & size"),  # (lane, column, label)
         (1, 2, "Build change"), (2, 3, "Deploy"), (0, 4, "Accept")]
INK, LANE_FILL, BOX = RGBColor(0x1F, 0x2A, 0x44), RGBColor(0xF2, 0xF4, 0xF7), RGBColor(0x00, 0x5E, 0xB8)
WHITE = RGBColor(255, 255, 255)
L, T, LANE_H, HEAD_W, COL_W = Inches(0.5), Inches(1.4), Inches(1.6), Inches(1.6), Inches(2.2)

prs = Presentation()                                      # use the host template here
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title; title.text = "Every change reaches the client in five hand-offs"
title.left, title.top, title.width, title.height = L, Inches(0.4), prs.slide_width - 2 * L, Inches(0.8)
title.text_frame.paragraphs[0].runs[0].font.size = Pt(24)  # titles 20-24 pt
fig = slide.shapes.add_group_shape()                      # one group: the figure moves as one

def unstyle(shape):
    # python-pptx's default style adds a theme shadow in some renderers
    sp = shape._element; st = sp.find(qn('p:style'))
    if st is not None: sp.remove(st)

def box(shape, x, y, w, h, text, fill, color, size, bold=False):
    s = fig.shapes.add_shape(shape, x, y, w, h); unstyle(s)
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.fill.background()
    r = s.text_frame.paragraphs[0].add_run(); r.text = text  # no font.name: theme fonts
    r.font.size, r.font.bold, r.font.color.rgb = Pt(size), bold, color
    return s

for i, name in enumerate(LANES):                          # lane band + header
    y = T + i * LANE_H
    box(MSO_SHAPE.RECTANGLE, L, y, HEAD_W + COL_W * 5, LANE_H - Inches(0.08), "", LANE_FILL, INK, 12)
    box(MSO_SHAPE.RECTANGLE, L, y, HEAD_W, LANE_H - Inches(0.08), name, INK, WHITE, 14, True)

nodes = [box(MSO_SHAPE.CHEVRON if c in (0, 4) else MSO_SHAPE.ROUNDED_RECTANGLE,
             L + HEAD_W + c * COL_W + Inches(0.2), T + lane * LANE_H + Inches(0.45),
             COL_W - Inches(0.4), Inches(0.62), label, BOX, WHITE, 12)
         for lane, c, label in STEPS]

for a, b in zip(nodes, nodes[1:]):                        # connectors glued to the boxes
    c = fig.shapes.add_connector(MSO_CONNECTOR.ELBOW, 0, 0, 0, 0); unstyle(c)
    c.begin_connect(a, 3); c.end_connect(b, 1)
    c.line.color.rgb, c.line.width = INK, Pt(1.5)
    ln = c.line._get_or_add_ln(); ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle"}))

# gate / milestone: dashed vertical line across all lanes at a stage boundary, label below the lanes
gx = L + HEAD_W + 3 * COL_W                               # boundary before column 3
gate = fig.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, gx, T - Inches(0.1), gx, T + len(LANES) * LANE_H)
unstyle(gate)
gate.line.color.rgb, gate.line.width, gate.line.dash_style = INK, Pt(1.5), MSO_LINE.DASH
tb = fig.shapes.add_textbox(gx - Inches(1.1), T + len(LANES) * LANE_H, Inches(2.2), Inches(0.35))
p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
g = p.add_run(); g.text = "Gate: go-live approved"; g.font.size, g.font.color.rgb = Pt(12), INK

prs.save("swimlane.pptx")
```

**Verify:** `unzip -p swimlane.pptx 'ppt/slides/slide*.xml' | grep -c '<p:pic>'` prints `0`; round-trip to an image (§4 command) and squint; every label is selectable text.
