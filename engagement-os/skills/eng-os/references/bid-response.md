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

## Match the buyer's required format

**This is the last step, once the content is reviewed and approved** — assembling section
markdown into whatever the buyer demands: a Word volume set, a slide deck, a portal form.

Follow the RFP's mandated response structure, volume split, page/word limits, and forms **exactly**
— non-compliance with format is a common auto-reject. If the RFP gives a response template, use it;
don't impose our own structure (the pursuit-side version of the "match the host-deck template" rule).

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
