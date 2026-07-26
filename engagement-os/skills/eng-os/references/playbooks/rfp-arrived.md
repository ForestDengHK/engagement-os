# Playbook: an RFP / tender arrives (the pursuit loop)

The bid lifecycle, from a tender landing to a submission-ready response. Each step names the
skill that owns it — follow that skill, don't reproduce it here. Runs in the `01_pursuit/<ENG-ID>/`
tree (`eng-scaffold --mode pursuit`; no delivery block is needed to bid).

## The shape: a spine, a loop, and two one-way gates

**This is not a waterfall.** Material arrives over weeks in an order you do not control — an
appendix here, a buyer clarification there, a case study someone finally digs out, a benchmark
you only think to look for once you are half-written. A plan that says "gather everything, then
analyse, then write" describes a bid nobody has ever run.

```
   the tender pack                    ┌───────── the loop, per arrival ─────────┐
   (you always get                    │                                          │
    this one first)                   │   material arrives                       │
         │                            │        ↓                                 │
         ▼                            │   ingest → canonical → matrix rows move  │
   ingest → analyse → GO/NO-GO 🛑 ────┤        ↓                                 │
         │                            │   the sections it touches get written    │
         ▼                            │   or revised → reviewed                  │
   compliance_matrix.md ◄─────────────┤                                          │
   (the spine, always current)        └──────────────────────────────────────────┘
                                                       │
                                        every section reviewed-r2/approved
                                                       ▼
                                                   SHIP 🛑 render, once, last
```

- **The spine** — `compliance_matrix.md`. One row per requirement, always current. It is what
  *"how far along are we"* means; no other artefact answers that question.
- **The loop** — runs once per arrival, any number of times, in any order. Analysis is not a
  phase that completes; each arrival re-opens it a little.
- **Two one-way gates** — the go/no-go (early, human) and the ship gate (last). Everything
  between them is the loop.

---

## Start — the tender pack

The one thing you reliably have on day one. It unblocks everything else, so it goes first and
alone; don't wait for the rest of the material to arrive.

1. **Ingest it** → [new-source-arrived.md](new-source-arrived.md) — the tender pack, its
   appendices, schedules, pricing workbook and draft contract go to
   `01_pursuit/<ENG-ID>/1_received/` (never edited) and come out as anchored markdown in
   `1_received/_md/`, citable by clause/page. The lossless image rule applies: a figure carrying
   a requirement is not allowed to disappear silently.
2. **Check the procurement route** — planted in `rfp_analysis.md` by the scaffolder's
   `--variant`. A **framework mini-competition** changes the loop: the buyer is pre-qualified,
   so the go/no-go shrinks to capacity + conflict of interest; call-off terms are pre-agreed
   (commercial risk review is narrower, not absent); and there may be **no clarification
   window** — check before planning step 5.
3. **Analyse it** → `eng-rfp-analyze`. Every requirement extracted with an ID + clause cite into
   `compliance_matrix.md`; the **scope decomposed into S-IDs with effort drivers** and a cited
   volumetric baseline; **our understanding and our solution** per client challenge, including
   what it does *not* solve; evaluation weights mapped; multi-role read; evidence-backed
   win-themes; risks and deal-breakers; the **materials-needed list** (research vs upload); a
   go/no-go. This is the spine's first version, not its last.
4. **Check for a prior bid — before drafting anything.** A re-issue, a follow-on, or the same
   buyer asking again means most of the answer already exists *and already survived an
   evaluation*. Convert it (`eng-ingest-source` → `01_pursuit/archive-<PRIOR-ID>/`) and fill
   `bid_reuse_analysis.md`: per section, FULL REUSABLE / PARTIAL / REQUIRES UPDATE / NEW, with a
   field-level diff of the old clause against the new one.
   **If there is none, create no file** — write *"searched X, none found"* into `rfp_analysis.md`
   §9 instead. A speculative reuse analysis reads as completed work and the next reader trusts
   it; a recorded negative is a checked fact.
4b. **Size it** → `eng-estimate` (priced tenders — i.e. nearly all of them). The S-ID table
   becomes a bottom-up effort model, the client-side hours ask, itemised contingency, and a
   cost→price build; where the buyer publishes a cost formula, price converts to marks
   arithmetically. Do this **before** the go/no-go: "can we win it at a price above our cost
   base" is a go/no-go question, and it cannot be answered by feel.
5. **Index what we hold** → `eng-index-assets` → `01_pursuit/_shared/firm_assets.md`. What each
   asset **proves** (the claim an evaluator scores, not the title), its date, whether it is
   **in-window** against this tender's recency rule, and its permission constraints. This is
   what makes the gap list real: a requirement covered by an indexed, in-window asset is a
   **citation, not a gap**. Undated is unusable — recency rules are pass/fail.
6. **Raise clarifications before the query deadline** → `eng-rfp-analyze` step 6b →
   `clarification_log.md`. Questions are **derived by a dimension sweep** (scope · solution ·
   evidence/qualification · commercial · delivery · evaluation-process), then run through the
   multi-role lens (`panel-discuss` if installed), then **the human decides what actually
   goes** — some questions reveal more about our position than the answer is worth. The query
   deadline is **earlier than the submission deadline** and it is hard: afterwards an ambiguity
   can only be handled by stating an assumption, which scores worse than an answer. Buyer
   answers are circulated to all bidders and become part of the tender documents — they
   re-enter through the loop like any other arrival.

**🛑 GO / NO-GO — human.** No-go: stop, log the rationale. Go-if: resolve the conditions first.
This gate exists so research and writing effort is never sunk into a bid we won't win or
can't deliver.

---

## The loop — run this once per arrival, for as long as material keeps coming

Every arrival is the same five moves, whatever it is: a buyer clarification, a sector benchmark,
a case study, a CV, an answer to a question you raised.

1. **File it by where it came from, never by what it is about.** A benchmark we downloaded and a
   case study we wrote are both "sector reference material", and only one may be freely quoted.

   | What | Where |
   |---|---|
   | this tender's pack | `01_pursuit/<ENG-ID>/1_received/` |
   | given to us or found by us | `_sources/pre_award/` (buyer-specific) · `_sources/public/` (sector-wide) |
   | **our own** reusable assets | `01_pursuit/_shared/<kind>/` — see its `README.md` |

   **Nothing from `_sources/engagement/` may be cited in a bid** — not this engagement's, not
   another client's. `eng_lint.py` enforces the boundary.

2. **Ingest and canonicalise** → [new-source-arrived.md](new-source-arrived.md), which owns
   bucketing → `eng-ingest-source` → `eng-update-canonical`. **A bid needs the canonical pair as
   much as a delivery does**: each bucket's `00_REFERENCE_SUMMARY.md` (facts, cited) and
   `01_REFERENCE_INSIGHTS.md` (what it means for us) are where a fact lands once instead of
   being re-read out of the source every time a section needs it.
   *Our own* assets don't go through the buckets — they go to `eng-index-assets`, which gives
   each one a row in `01_pursuit/_shared/firm_assets.md`. An asset nobody indexed is one nobody
   finds under deadline, and one `eng_lint.py` will fail the moment a section cites it.

3. **Move the spine.** Which matrix rows does this arrival close, weaken, or newly expose? A
   requirement covered by an indexed, in-window asset is a **citation, not a gap** — this is why
   the assets index has to exist before you can trust the gap list. Gaps that survive are the
   scope for `eng-bid-research`, which closes them with cited findings in `bid_research_log.md`
   (`[T3:OWN]` for our own research) — zero fabrication, and anything unsourceable is marked
   `[⚠VERIFY]` and kept out of the response.

4. **Write or revise the sections it touches** → `eng-bid-respond`. Only the sections whose
   `answers_reqs` include the moved rows. Sections are built *from the matrix*, not free-written.

5. **Review what you touched.** Per section, not per document — that is the point of the next
   section of this file.

---

## The unit of work: one markdown file per response section

`3_drafting/sections/`, named for the buyer's own section numbering. Separate files, not one
growing document, because each section is **scored separately, reviewed separately, and revised
on its own clock** — a single document hides which parts are finished and forces every review to
re-read everything.

Each file's frontmatter carries what it is accountable for: which requirements it answers, which
assets it cites, its page budget, its figures, and its **status** — `draft → reviewed-r1 →
reviewed-r2 → approved`, branching to `revise-r1` / `blocked-r1` with a `blocked_on` reason.
The fields and vocabulary are defined once in `references/section-contract.md`; the template
plants them, `eng_lint.py` enforces them, `eng-render` gates and strips by them.

**Two rounds, not one gate** — the status vocabulary carries the round for a reason:

- **R1 — panel red-team** (`panel-review` if installed, else a manual evaluator / legal /
  finance / architect pass): *does this score?* Against the scoring note in the frontmatter,
  not against taste.
- **R2 — experienced human**: what only experience sees — the claim that will draw a question
  we cannot answer, the tone that reads wrong to this buyer, the omission a scorer will punish.

This is where the review effort goes, and it goes there **continuously** — a section reaching
`reviewed-r2` early is finished early and stops consuming attention. The alternative is reading
a finished document for the first time the night before submission.

---

## Ship — once, last 🛑

The output format is the *last* step, not a thing you build toward incrementally.

1. **Check** → `eng-check` (`--strict` before a freeze). It runs the gates and reports what is
   blocking; nobody types a script path to reach them.
2. **Freeze** to `4_final/`; record the submitted version + date.
3. **Render** → `eng-render --profile bid`, which refuses to build unless every section is
   `reviewed-r2`/`approved` and no `[⚠VERIFY]` survives in body text, then strips the internal
   scaffolding and produces the buyer's required format (`verify_deck.py` if it is a deck).

## Stop gates

- **STOP at the go/no-go** on a no-go.
- **STOP and surface to the human** if research cannot source a claim a win-theme depends on
  (`[⚠VERIFY]` on a load-bearing claim) — that is a go/no-go re-check, not a wording fix.
- **STOP before submission** if any mandatory requirement is not `met` or any format rule is
  breached — format non-compliance is a common auto-reject. `eng-check` decides the
  mandatory-row check, the `[⚠VERIFY]`-in-a-frozen-response check, and the bucket-leak check
  without a human re-reading the whole response. Run it throughout, not only here: a bucket
  leak found on the day it happens is a one-line fix.
