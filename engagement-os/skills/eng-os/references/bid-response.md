# Bid response assembly

How to turn a validated analysis + sourced research into a compliant, persuasive, fully
traceable response — every requirement answered, every claim sourced, red-teamed before it ships.

## Contents
- The core move: requirement-driven, not narrative-driven
- Draft per section, in markdown, before any output format
- Figures: build them with the section, not at the end
- Review rounds, not a review
- Match the buyer's required format
- Compliance first, persuasion second
- Weaving win-themes with proof
- Traceability of every claim
- The panel red-team gate
- Versioning & submission mechanics

## The core move: requirement-driven, not narrative-driven

The response is assembled **from the compliance matrix**, not free-written. Every requirement row
maps to a response section that answers it; when the matrix closes (every row `met`, every
mandatory satisfied), the response is complete. This is the pursuit-side analogue of building a
deliverable from validated findings: the matrix is the fact base, the response adds the persuasion.

## Draft per section, in markdown, before any output format

**One markdown file per response section**, in `3_drafting/sections/`, named for the buyer's own
section number. Not one document — separate files, because each section is scored separately,
reviewed separately, and revised on its own clock. A single growing document hides which parts
are finished and forces every review to re-read everything.

Each file opens with frontmatter carrying what the section is accountable for:

```yaml
section: "5.1.3 Q1 — Key Deliverables"
rft_clause: "§Section 60"
marks: 180
pass_mark: 90
scoring: "each deliverable assessed individually, out of 30"
answers_reqs: [R-013]
page_budget: "shared 5 A4 across 5.1.3 Q1-Q3, Arial 10"
figures: [F-01]
evidence: [A-001, A-002]
status: draft
```

`scoring` earns its place: a section marked **per item** must satisfy the criteria per item — six
deliverables scored out of 30 each means six self-contained answers, and a flowing narrative that
blurs them loses marks six times. That instruction is in the RFT and is easy to read past.

**Do not think about the output format while writing.** Content and rendering are separate jobs,
and mixing them costs both: you trim an argument to fit a slide before knowing whether the
argument is right. Get the content correct and reviewed first; §"Match the buyer's required
format" is the *last* step, not the first.

**Track the page budget as you go, though** — it is the one format constraint that changes what
you write rather than how it looks. Note whether the limit is **per question or shared across
questions**: an RFT saying "max 5 A4 pages for 3 questions" is a shared budget, while "max 3 A4
pages per question response" is not, and the two are easy to confuse in the direction of writing
too much. At Arial 10, roughly 500-550 words fill one side of A4; a full-width figure costs about
half a page.

## Figures: build them with the section, not at the end

If a section needs a figure, build it while writing that section — a figure decided afterwards
becomes decoration, and a figure that would have carried the argument gets replaced by three
paragraphs that do it worse.

**Use the `designing-figures` skill.** Do not hand-draw. Its first rule is the one that matters:
pick the archetype from the message before drawing anything. Hand-rolling this for real produced
the anti-pattern the skill names explicitly — a flat row of boxes — when the message ("six
deliverables, each scored individually, together covering the buyer's own eleven limitations")
called for a **coverage grid**. Swapping the archetype changed what the figure proved; that is the
test for having picked the right one.

### Three artefacts per figure, one source

| File | What it is | Who uses it |
|---|---|---|
| `F-0x_<name>.html` | **the source** — edit here, re-render | whoever revises the figure |
| `F-0x_<name>.png` | raster at 2× | drops into the response document |
| `F-0x_<name>.pptx` | **one slide, native editable shapes** | a reviewer who wants to correct it in PowerPoint |

A flattened image is not enough: review rounds produce figure corrections, and a reviewer who
cannot edit sends the change back as prose instead. Generate the PPTX from the same HTML, so the
three never diverge.

```bash
cd 3_drafting/figures && (python3 -m http.server 4321 &) ; sleep 1
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1920,1080 --default-background-color=FFFFFFFF \
  --screenshot=F-01.png "http://localhost:4321/F-01.html"
node ~/.claude/skills/baoyu-design/agents/gen-pptx/dist/cli.mjs \
  --url "http://localhost:4321/F-01.html" --config cfg.json --out .
pkill -f "http.server 4321"
```

### What breaks the editable export

- **No CSS pseudo-elements or masked icons.** `::before` / `::after` and `mask`-recoloured icons
  do not convert. Draw dots, bullets and markers as **real elements** (`<i class="dot">`) —
  otherwise they vanish from the PPTX while looking fine in the PNG.
- **Text that fits in HTML can clip in the export.** PowerPoint's text metrics differ, so a label
  sized to its box in the browser loses its last characters as a shape. Found for real:
  "CARRIES THE DECISION" arrived as "CARRIES THE DECISIO".
- CSS gradients become a picture, not a shape. Fine for a brand bar; don't rely on one for content.

### Verify both outputs, every time

Look at the PNG **and** round-trip the PPTX back to an image before moving on:

```bash
soffice --headless --convert-to pdf F-01.pptx --outdir /tmp/v && pdftoppm -png -r 100 /tmp/v/F-01.pdf /tmp/v/rt
```

Then confirm it is genuinely editable rather than a flattened page:

```bash
python3 -c "from pptx import Presentation; s=Presentation('F-01.pptx').slides[0]; \
print(len(s.shapes),'shapes;',sum(1 for x in s.shapes if x.has_text_frame and x.text_frame.text.strip()),'with text')"
```
A one-slide export with 1-2 shapes is a screenshot in a wrapper. The figure above came out as 174
native shapes, 44 of them carrying editable text.

## Review rounds, not a review

A section is not finished when it is written; it is finished when the rounds stop producing
changes. Each section carries its own review log — one row per pass — because sections finish at
different times and a single project-wide gate hides that.

| Round | What it catches |
|---|---|
| **R1 — panel red-team** | Does it score? Multi-lens: evaluator, legal, finance, delivery |
| **R2 — experienced human** | What only experience sees: a claim that will not survive a client conversation, a promise delivery cannot staff, a tone wrong for this buyer |
| **R3 — final read** | Consistency across sections, format compliance, nothing left `[⚠VERIFY]` |

Do not collapse R1 and R2. They fail differently: R1 is structural and can be reasoned about from
the RFT; R2 is judgement and cannot.

## Match the buyer's required format

**This is the last step, once the content is reviewed and approved** — assembling section
markdown into whatever the buyer demands: a Word volume set, a slide deck, a portal form.

Follow the RFP's mandated response structure, volume split, page/word limits, and forms **exactly**
— non-compliance with format is a common auto-reject. If the RFP gives a response template, use it;
don't impose our own structure (the pursuit-side version of the "match the host-deck template" rule).

Rendering mechanics: the `docx` / `pptx` skills own the output artefact. Figures go in as the PNG
rendered from their SVG source, never as a screenshot; the SVG stays in `figures/` so the next
version regenerates rather than being redrawn. Re-check the page count **after** rendering — a
word-count estimate is an estimate, and the limit is measured in pages of the delivered file.

## Compliance first, persuasion second

- Every **mandatory** requirement is fully and unambiguously met; state compliance explicitly.
- Where we take an exception or partial, say so plainly with the rationale — never bury or fudge it.
- Only once compliance is secured do win-themes and differentiation earn the extra points.

## Weaving win-themes with proof

Carry the 3–5 win-themes from the analysis through the response, each **backed by the sourced
evidence** in the research log (a named engagement, a measured outcome, a real credential). Land
them where the high-weight evaluation criteria are scored. A theme without proof in the log gets
cut — no slogans.

## Traceability of every claim

Same discipline as the whole pack: every factual claim in the response traces to either an
`[RFP §x]` requirement or a cited item in `bid_research_log.md` (`[T3:OWN]` external / an internal
document for firm credentials). A reviewer must be able to open the source behind any number,
credential, or outcome. **No unsupported claim, no fabricated credential — ever.** Anything still
`[⚠VERIFY]` is cut or closed before submission, never shipped.

## The panel red-team gate (not optional)

Before submission, red-team the response — with the Panel Framework if installed, else a manual
multi-lens pass:

- **Evaluator's eye** — would this actually score the points? Is every criterion answered?
- **Legal / contracts** — are exceptions stated cleanly; any exposure in what we've committed?
- **Finance / commercial** — is anything promised that we can't price or deliver at margin?
- **Solution architect / delivery** — is what we've written actually deliverable as staffed?

Red-line findings are fixed before the version is called submission-ready.

## Versioning & submission mechanics

Version openly: `SKELETON → v0.1 … → v1.0 (submitted)`. A `SKELETON` carries structure only (no
real content). Keep drafts in `3_drafting/`; the frozen submitted set goes to `4_final/` and is
recorded in `DELIVERABLES.md` (or the pursuit equivalent) with the submission date. Never edit a
submitted volume in place — a post-submission change is a new version with a dated note.
