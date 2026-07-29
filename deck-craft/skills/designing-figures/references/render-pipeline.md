# Render Pipeline — HTML/CSS → PNG / editable PPTX

Render exhibits as **HTML/CSS** (best grid + real icons + browser preview), then capture to PNG (deck asset) or export to editable PPTX. This beats hand-placing shapes in pptxgenjs for anything with a grid or real icons.

## 1. Canvas conventions

- One self-contained `.html` per exhibit. Canvas **1920×1080** (16:9, matches a slide). `body{width:1920px;height:1080px}`.
- `@import` the brand font (Google Fonts) at the top; system fallback in the stack.
- Tokens as `:root` CSS variables (copy `assets/brand-tokens.css`).
- Layout with **CSS grid / flex + `gap`** — never absolute-position a grid by hand. Reserve absolute positioning for diagram overlays (connectors, callouts).
- Standard furniture: left brand bar, kicker, action title / key-message band, the exhibit, legend + source footer (see the `examples/`).
- Icons via CSS mask (see `visual-system.md` §5); icon files in an `icons/` folder beside the HTML.
- For Sankey/flow: use an inline `<svg>` for ribbons (cubic-bezier bands), HTML labels on top. See `examples/example_flow_sankey.html`.

## 2. Render to PNG (headless Chrome)

Serve the folder, screenshot at 1:1. PNG is the asset most decks (and pptxgenjs/python-pptx builds) consume.

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
# config: {"width":1920,"height":1080,"slides":[{"showJs":"document.querySelector('deck-stage').goTo(0)","selector":"deck-stage > [data-deck-active]"}],"resetTransformSelector":"deck-stage","filename":"exhibit"}
node $SK/agents/gen-pptx/dist/cli.mjs --url <servedDeckUrl> --config <json> --out <dir>
```
**Conversion caveats:** CSS `::before` / `::after` and `mask`-recoloured icons do NOT survive the editable export — draw dots, bullets and markers as **real elements** (`<i class="dot">`) or they vanish from the PPTX while looking fine in the PNG. Text metrics differ from the browser: a label that exactly fits its HTML box can lose its last characters as a PowerPoint shape (found for real: "CARRIES THE DECISION" → "CARRIES THE DECISIO") — leave headroom or shorten the label. CSS gradients become a picture, not a shape (fine for a brand bar, not for content). For exhibits that rely on masked icons, prefer **PNG placement** (render §2, drop the PNG on the slide) over editable conversion. Plain shapes, text, real `<img>`, and SVG ribbons convert fine.

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
| Figure inside an existing deck/report build (pptxgenjs/python-pptx/Markdown) | **PNG** (§2) — drop into the build's image folder. **Default. No baoyu.** |
| A standalone editable PowerPoint of the figure/deck | baoyu editable export (§4), PNG-placing any masked-icon figures |
| Quick review with the user | PNG (§2) or serve the HTML and share the URL |

## 6. Editing model — the HTML is the master, never the PNG

The PNG/PPTX is an **output**, not the editable source — exactly like a draw.io `.png` is an export of a `.drawio`. To change a figure:

1. **Edit the HTML source** (labels, numbers, colour are plain readable text — easier to edit than draw.io XML).
2. **Re-render** (§2) → fresh PNG, and rebuild the deck if it embeds the PNG.

Keep the figure HTML in the repo beside the deck/diagram sources (e.g. next to existing `.drawio` files) so it is version-controlled and re-renderable.

**Two editing modes for the consumer:**
- **Edit via source (default):** you/the team change the HTML and re-render. Best quality, full control. The client receives a PNG in the deck (cannot edit it in PowerPoint — same as today's draw.io exports).
- **Edit in PowerPoint:** only if the client must hand-edit — use baoyu editable export (§4) to get native shapes/text. Trade-off: masked icons don't convert. Prefer this only when in-app editing is a hard requirement.
