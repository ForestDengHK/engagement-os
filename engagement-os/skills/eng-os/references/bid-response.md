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
mandatory satisfied), the response is complete.

Two things a real matrix does that the neat version does not. **A third of it is not prose.**
Submission mechanics, the query deadline, and the terms accepted by tendering are obligations on
the bid process, not questions — each belongs to a named control (a submission control sheet, the
clarification register, commercial sign-off, partner-level contract acceptance) recorded in the
outline. Inventing a response section for "submit by 12:00" is how a compliance matrix starts
lying. **And a requirement can be scored twice** — a roadmap graded under Deliverables and again
under Methodology — so the outline names a primary section and a second one rather than dropping
the row. Coverage (every row appears somewhere) is machine-checked; placement is judgement. This is the pursuit-side analogue of building a
deliverable from validated findings: the matrix is the fact base, the response adds the persuasion.

## Draft per section, in markdown, before any output format

**One markdown file per response section**, in `3_drafting/sections/`, named for the buyer's own
section number. Not one document — separate files, because each section is scored separately,
reviewed separately, and revised on its own clock. A single growing document hides which parts
are finished and forces every review to re-read everything.

Each file opens with frontmatter carrying what the section is accountable for (illustrative
values — the real ones come from THIS tender's RFT, never from an example):

```yaml
section: "3.2 Q1 — Example Section"
rft_clause: "§Section 12"
marks: 40
pass_mark: 20
scoring: "each item assessed individually, out of 10"
answers_reqs: [R-007]
page_budget: "3 A4 shared across 3.2 Q1-Q2, Arial 10"
figures: [F-01]
evidence: [A-004]
status: draft
```

The fields, the status vocabulary, the scaffolding markers and the figure rule are defined ONCE
in `references/section-contract.md` — the template plants them, `eng_lint.py` enforces them,
`eng-render` gates and strips by them. `answers_reqs`, `evidence` and `figures` are
cross-checked against their registers; an id naming nothing is an error.

`scoring` earns its place: a section marked **per item** must satisfy the criteria per item — six
deliverables scored out of 30 each means six self-contained answers, and a flowing narrative that
blurs them loses marks six times. That instruction is in the RFT and is easy to read past.

**Do not think about the output format while writing.** Content and rendering are separate jobs,
and mixing them costs both: you trim an argument to fit a slide before knowing whether the
argument is right. Get the content correct and reviewed first; §"Match the buyer's required
format" is the *last* step, not the first.

**Track the page budget as you go, though** — it is the one format constraint that changes what
you write rather than how it looks. And track it in **both** directions: the buyer scores "the
level of detail provided", so an unused half of a 5-page budget on a 280-mark criterion is marks
left on the table, not discipline. Measuring it before approval means rendering one section on its
own with `--profile bid --force` (which reports what it overrides); the `plain` internal review
copy keeps the scaffolding and therefore does not measure the buyer's page count. Note whether the limit is **per question or shared across
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
deliverables, each scored individually, together covering the limitations the buyer itself listed")
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

**The caption is client-facing; the pointer to the master is not.** Name the `.html` and `.pptx`
on a `**Figure source.**` line, which the render strips — a caption survives the strip, so a
caption naming `F-01_x.html` prints our internal filenames on a tender page (that happened, from
the pack's own template).

**A figure for an A4 document is not a slide.** Keep `designing-figures`' canvas, grid and tokens,
but drop the furniture the document already supplies: the section heading, and a source footer the
markdown caption repeats. On A4 portrait a 16:9 exhibit lands at roughly a third of a page, which
is the right budget for one — two full-width figures and half the page is gone.

**The mechanics — canvas conventions, the headless-Chrome render, the editable export, and the
verification of both outputs — live in `designing-figures/references/render-pipeline.md`. Do not
copy them here; that document owns them, including the traps this pack hit the hard way
(pseudo-elements vanishing from the export, text clipping on PowerPoint metrics, the collapsed
footer, the stale-PNG trap). The pack-specific policy is only what is above: three artefacts,
one HTML source, figure ids from the contract.**

## Review rounds, not a review

A section is not finished when it is written; it is finished when the rounds stop producing
changes. Each section carries its own review log — one row per pass — because sections finish at
different times and a single project-wide gate hides that.

| Round | What it catches |
|---|---|
| **R1 — panel red-team** | Does it score? Multi-lens: evaluator, legal, finance, delivery |
| **R2 — experienced human** | What only experience sees: a claim that will not survive a client conversation, a promise delivery cannot staff, a tone wrong for this buyer |
| **R3 — final read** | Consistency across sections, format compliance, nothing left `[⚠VERIFY]` |

A round that sends the section back and is then re-run is **two rows**, appended: `R1` with
`revise`, then `R1 (2nd pass)` with `pass`. Overwriting the first row to satisfy the status check
erases exactly what the log is for. R2 is a *human* round by definition — an agent that marks its
own R2 has removed the gate rather than passed it, so a section drafted end-to-end by an agent
tops out at `reviewed-r1`.

Do not collapse R1 and R2. They fail differently: R1 is structural and can be reasoned about from
the RFT; R2 is judgement and cannot.

## Use the buyer's own response form — do not design your own

Before a word is written, read what the buyer supplied. A real tender carries most of the answer
scaffolding already, and on the pack's own worked example (GNI 26-002) that meant **51 Yes / No /
N-A answer boxes, four "TENDERER'S RESPONSE (identify document attached)" boxes and five appendix
forms** — none of which the first draft reproduced, because nothing told it to look.

Three modes, declared per section in `response_form`:

| Mode | What the buyer gave | What we do |
|---|---|---|
| `buyer-form: <file>` | A form to fill — reference data sheet, CV sheet, pricing workbook, declaration | Fill **their file** through `docx` / `xlsx`. Re-typesetting it in our own layout is the error: the evaluator is checking against their template |
| `buyer-structure` | Numbered questions and the answer options (Yes / No / N-A) | Reproduce their numbering and wording exactly, then answer under each. A tidier table of our own makes them hunt |
| `prose` | A response box and a page limit | Our document, written to the page budget and identified in that box |

The scaffolding is already in the repo: `eng-ingest-source` converted the RFT to markdown under
`1_received/_md/`, so lifting the structure is reading, not parsing. `eng_lint` flags a section
whose clause carries answer boxes but which was written as free prose
(`response-structure-invented`), and a `buyer-form` that names no file.

### Filling their form is the work, not describing it

A `buyer-form` answer is finished when **their file is filled**, in `3_drafting/forms/` — a working
copy, because `1_received/` must stay exactly as issued or the repo loses its evidence of what the
buyer actually sent. The section that declares the mode is a **cover note**: what was filled, what
is still owed, who signs it. It is not a prose restatement of the form, and the two are easy to
confuse when the form is somewhere else and the markdown is in front of you.

**A form is often a table inside their document, not a separate file.** This tender attaches its
pricing workbook but keeps the Project Reference Data Sheet and the CV Reference Data Sheet as
tables inside the RFT itself — and a markdown conversion carries the *reference* to them without
carrying the *form*. Extract the table into a working copy and fill it in their field order; the
labels and their sequence are exactly what an evaluator checks against.

The worked example is stark: this tender's whole price response is **two cells** — the tenderer's
name on the cover sheet and one lump sum on the pricing sheet, which the workbook then totals into
the Form of Tender. The first draft answered it with 565 words of prose about the pricing approach
and left both cells empty. Every one of those words was unreadable by the evaluator, who opens the
workbook.

**Why this is not pedantry.** Format non-compliance is one of the few ways to lose a tender before
the content is read at all. A pass/fail questionnaire re-organised into our own table risks an
evaluator recording "did not answer question 3" against an answer that is on the page.

## Match the buyer's required format

**This is the last step, once the content is reviewed and approved** — assembling section
markdown into whatever the buyer demands: a Word volume set, a slide deck, a portal form.

Follow the RFP's mandated response structure, volume split, page/word limits, and forms **exactly**
— non-compliance with format is a common auto-reject. If the RFP gives a response template, use it;
don't impose our own structure (the pursuit-side version of the "match the host-deck template" rule).

### What the reader may never see

The response is written in an internal shorthand and **delivered in the buyer's language.** An
evaluator who reads `A-014`, `[App5 cl.6; Sch.4]` or `[⚠VERIFY — the referee is unconfirmed]` in a
submitted volume is not reading a draft; they are reading a document that was never finished, and
they price that impression into every judgement that follows. `eng-render` performs the conversion
(clause refs into the buyer's vocabulary, unresolved facts into a neutral `[TBD]`, internal ids
deleted) — but the conversion is a safety net, not a licence: a sentence whose evidence is an id
loses its evidence on delivery, so name the thing in words and keep the id on the traceability line.

**And `[TBD]` is a real answer, used sparingly.** On a pass/fail questionnaire it is honest — the
attestation is owed, and inventing "None" would be worse. On a scored answer it costs marks, so a
`[TBD]` still in a scored section at submission is a decision to score zero on that point, taken
deliberately or not at all.

### Assembling

**Hand off to the `eng-render` skill** with `--profile bid`. Rendering is a separate,
independently invokable step — it works on any directory of markdown and knows nothing about
tenders except what the profile tells it. Don't concatenate by hand: the strip is fiddly and the
failure is invisible (internal scaffolding reaching an evaluator).

What it strips, what it refuses to build on, and how typography is enforced are owned by
`eng-render`'s SKILL.md and the section contract — not restated here, because a copied policy
rots. The one thing worth knowing at this desk: every refusal exists because it was a real
defect first (a figure silently degraded to alt text; an unfixed R1 verdict reaching the
evaluator; an open `[⚠VERIFY]` shipped as a claim), and `--force` exists for working drafts,
never for submissions.

Re-check the page count **after** rendering — a word-count estimate is an estimate, and the limit
is measured in pages of the delivered file.

### If the buyer wants slides

**A deck is a different artefact, not a reformat of the response.** A response section is prose
sized to a page budget: paginate it and it overflows onto untitled continuation slides and orphans
the figure captions onto slides of their own.

So `eng-render --to deck-manifest` emits a manifest and hands off to `presentation-builder`, which
re-cuts the argument into one message per slide and produces the editable export. The manifest
carries each figure's `.html` source and editable `.pptx` alongside the `.png`, so the deck stays
correctable rather than flattened.

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
