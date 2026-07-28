# Image triage — deciding what a figure carries

`convert_source.py` extracts every image it cannot **prove** decorative from the bytes and tags
it `[uncertain]`. Deciding which of those carry information is a vision + judgment task. This is
the method for doing it, shared by `eng-ingest-source` (sourced material) and `eng-index-assets`
(our own assets) so the two cannot drift.

## Why this needs a method and not an instruction

The instruction used to be one line — "triage every extracted image, OCR the uncertain ones".
On the real AIB case-study deck that line met 34 images at once, and the cheapest action that
satisfied it was to call them all `[decorative]` and delete them. That is what happened: 13
extracted, 13 deleted, including the as-is architecture diagram the whole case study rests on.
Nothing in the pack noticed, because a document whose figures were all deleted looked exactly
like a document that never had any.

Two things follow, and both are load-bearing:

- **Triage is batched work, not a per-file afterthought.** One deck is 34 images; one playbook
  used to be 296 before page components were consolidated. A pass that only works when someone
  is patient is a pass that does not run.
- **Deleting must cost something.** `--apply` refuses a `[decorative]` verdict with no reason
  and refuses a partial pass, and it writes a ledger. An image nobody looked at and an image
  someone judged must not end up in the same state.

The converter also keeps one representation of one figure. When a PDF page is rendered because
its diagram is assembled from vector/raster parts, the readable page snapshot is the content
figure; its circles, arrows, borders and thumbnails are not emitted as separate triage items.
The markdown records how many embedded components were consolidated into the snapshot. This is
lossless consolidation, not decorative classification: the complete page remains inline.

## What a kept figure must leave behind

**The markdown is the layer everything downstream reads.** A kept figure is an image followed by
an explanation of what that image says — written so that a reader of the markdown alone knows the
figure's content and never has to open it. Going back to the original is the exception, for
resolving a doubt; it is not the normal way to find out what a diagram shows.

So a caption is not a label. `*Figure 3*`, or the filename written out again, passes every check
that only tests for non-empty and tells a reader nothing. Say what is actually in it: which boxes
feed which, what the swimlanes are, what the axis runs over, what the rows say, what the figure
argues. `--apply` refuses anything under ~60 characters or that only repeats the filename.

**Whether to also transcribe the text depends on whether the markdown already has it**, and you
do not have to guess — `--worklist` prints `text already in the md: NN%` for every image:

| Overlap | Verdict | Because |
|---|---|---|
| ≥ 80% | `content` | The extractor already read this figure's words. Transcribing them again buries the page in noise. Caption what words cannot carry: the structure. |
| < 80% | `ocr-done` | The words exist only inside the image. Capture them verbatim or they are lost. |

`--apply` enforces this: an `ocr-done` whose text is already ≥80% in the page's prose is refused.
Measured on the AIB deck before the rule existed — **14 of 18 OCR blocks were 95–100% words the
markdown already had, three of them word-for-word duplicates**, roughly 5,000 wasted words that
pushed the real interpretation out of sight.

Tesseract is evidence, not authority. On small labels it can omit rows or substitute a plausible
word (a real global-delivery map read `AMS Centres` as `AWS Centres`). When overlap is low and
the figure is kept as `ocr-done`, compare the transcript against the rendered image and correct
those errors before applying it. The point is faithful text in markdown, not raw OCR output.

## The judgment: icon or diagram?

Size does not decide this, and neither does OCR. The AIB as-is architecture diagram is
**364×231 and 50KB** — smaller than several of the icons in the same deck — and `tesseract` read
**zero words** off it, because the labels are 4px type. An OCR-only filter deletes it. Only
looking at it works.

| Verdict | What it looks like | What to write |
|---|---|---|
| `[decorative]` | Logo, brand swoosh or gradient background, bullet glyph, rule, spacer, a lone line-art icon sitting beside a heading | A reason — *what it is*: "line icon — rosette in cupped hands", "pink brand swoosh, full-bleed title background" |
| `[content]` | Anything with structure a reader would have to look at: architecture diagram, roadmap/Gantt, org chart, chart with axes, a table rendered as an image, a screenshot | A caption: what it shows, **in the words of the surrounding clause**, plus the unit — "Target data architecture — lakehouse zones and consumers [Page 3]" |
| `[ocr-done]` | Content whose meaning is largely the text inside it, and that text did not survive extraction | The caption **and** the verbatim text, which `--apply` parks in a collapsible block |

Three rules that resolve most of the hard cases:

1. **A figure that recurs is still a figure.** A deck legitimately re-shows a diagram on a build
   slide or a recap. Repetition is not decoration; the converter already dropped what appears on
   *most* units.
2. **A brand background around a diagram does not make the diagram decorative.** Judge the
   content, not the frame.
3. **When unsure, `[ocr-done]`, never `[decorative]`.** Deleting is the only irreversible
   verdict. Capturing text costs a paragraph; a deleted scope diagram costs the estimate that
   was supposed to be built from it.

## Running it

```bash
TRIAGE=${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/triage_images.py

# 1. What is waiting, and the evidence to judge it: unit, dimensions, size, OCR hint,
#    and the markdown either side of where the figure sits.
python3 "$TRIAGE" --worklist <md_path>

# 2. Look at each image — Read renders it. Dispatch parallel vision subagents when the
#    worklist is long. Do NOT ask an agent to edit the markdown; verdicts come back,
#    --apply writes. Batch recipe below — it is not optional, it is what makes them finish.

# 3. Apply. Refuses a partial pass, a reasonless deletion, or a caption-less keep.
python3 "$TRIAGE" --apply <md_path> --verdicts <verdicts.json>
```

### Batching that finishes

A triage agent spends one turn per image, and agents have a turn budget. Measured on this deck:
**11–12 images per agent, told to read a reference file first → 2 of 3 agents died at the turn
limit** with their slices unjudged. Re-run at **5–6 images per agent, with the rules inlined in
the prompt and an explicit instruction to read every image in ONE message using parallel Read
calls → 4 of 4 finished, all 34 images judged in 94 seconds.** So:

- **5–6 images per agent.** Not 15.
- **Inline the verdict rules in the prompt.** An agent that must open this file first has spent
  turns it needed for images.
- **Say "read ALL your images in one message with parallel Read calls".** Left to itself an
  agent reads one per turn and runs out.
- **Give each agent the page context it needs** (what the deck is, what those slides cover) so
  it captions in the document's language without spending turns grepping the markdown.
- **Ask for one fenced ```json block and nothing else** — you are concatenating several agents'
  output into one verdicts file.

### Verdict format

`verdicts.json` is a list, one object per `[uncertain]` image:

```json
[
  {"image": "deck__p3_img3.png", "verdict": "content",
   "caption": "As-is data architecture — Teradata EDW and Cloudera Hadoop feeding risk, finance and BI consumers [Page 3]"},
  {"image": "deck__p13_img4.png", "verdict": "decorative",
   "reason": "line icon — rosette in cupped hands"},
  {"image": "deck__p12_img10.png", "verdict": "ocr-done",
   "caption": "Migration wave sequencing [Page 12]",
   "ocr": "Wave 1 — Risk Reporting · Wave 2 — Finance · Wave 3 — Customer"}
]
```

## When you cannot read the figure

If a figure's own labels are too small to read, do **not** caption it "see the source PDF" — that
is the trip back to the binary the md-first rule exists to prevent, and it leaves the fact
unreachable to everything downstream. The converter now renders the whole page whenever its
figures came out as unreadable thumbnails, so the legible version is usually sitting beside it as
`pN_page.png`; caption from that and mark the thumbnail `[decorative]` with the reason
"thumbnail of the page figure, kept at readable size in `pN_page.png`". Only when no legible
render exists does the caption say so plainly, and then it says *what is missing*, not just where
to look.

## What the pack checks afterwards

- `images-untriaged` / `images-uncaptioned` — a surviving `[uncertain]` tag or `[caption-needed]`
  stub means the pass did not finish.
- `images-unaccounted` — the converter recorded how many images it extracted; if they are gone
  and no ledger says who decided that, this errors. This is the rule that would have caught the
  AIB deck.

## Anti-goals

Do not classify from the filename, the dimensions, or the OCR hint alone — look at the image.
Do not delete an `[uncertain]` image before its text is captured. Do not hand-edit the markdown
to record verdicts: `--apply` exists so that 296 images do not become 296 chances to break a
link. And do not reach for an external OCR service — `tesseract` supplies the hint, vision
supplies the judgment, and neither needs an API key.
