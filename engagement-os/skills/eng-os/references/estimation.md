# Estimation method

How to turn a decomposed scope into a defensible effort model, a cost base, and a price posture —
bottom-up, cited, cross-checked, and honest about its own error bar.

## Contents
- Where estimation sits, and its one hard precondition
- The doctrine
- Step 1 — basis of estimate
- Step 2 — pick two techniques, and make them actually independent
- Step 3 — the effort model (role × grade × days, per S-ID)
- Step 3b — the overlap audit (the step that decides whether the number is inflated)
- Step 4 — client-side effort (theirs, not just ours)
- Step 5 — the range: two uncertainties, kept apart
- Step 6 — calibration, including the outside view
- Step 7 — contingency = P80 − P50
- Step 8 — cost → price (and never the reverse)
- Step 9 — price vs score: decision support, not a recommendation
- Step 10 — into the buyer's pricing document
- Step 11 — re-baseline triggers
- The artefact: one workbook, and a generated snapshot

## Where estimation sits, and its one hard precondition

```
ingest RFP ─► analyse (eng-rfp-analyze) ─┬─► §3 scope decomposition (S-IDs + volumetrics)
                                          │            │
                                          │            ▼
                                          │      ESTIMATE (eng-estimate → estimation.md)  ← this file
                                          │            │
                                          └─► §4 solution ─┘   ─► price posture → bid_response §pricing
```

**The precondition: a scope decomposition exists.** Estimating from RFP prose means estimating
the same sentence three different ways on three different days. If `rfp_analysis.md` §3 has no
S-ID table with effort drivers, stop and go build it — that is `eng-rfp-analyze` step 2b, and
it takes less time than reconciling three guesses.

The same method serves a delivery-side change request or a phase-2 proposal; only the input
document changes (SOW scope items instead of RFP S-IDs).

## The doctrine

- **The estimate informs the price. It does not set it.** Pricing is a commercial judgement that
  belongs to the partner: it weighs appetite for the client, competitive position, portfolio and
  risk tolerance — none of which live in this model. So the deliverable is **decision support**,
  not a recommended number: the range, what drives it, and what each candidate price costs in
  margin and in marks. An estimate that ends with "recommended bid price: €X" has quietly taken a
  decision that was never the estimator's to take, and it invites the reader to accept the number
  instead of interrogating it. Same discipline as clarification questions: the agent drafts, the
  human decides.
- **Every effort line traces to an S-ID.** An effort line with no S-ID means the scope table is
  incomplete. An S-ID with no effort line means we have quietly agreed to do something for free.
  Both are found by reading the two tables against each other, and only then.
- **Nothing fabricated — rates included.** A day rate, a productivity factor, or a benchmark that
  can't be sourced to the firm's rate card, an indexed asset, or a cited external reference is
  `[⚠VERIFY]`, not a number. The same rule that governs a capability claim governs money, and
  money is the claim that gets audited.
- **A single number is not an estimate**, and a *price* band is not a *range*. Publish the effort
  distribution — P50, P80, and the spread's cause. Presenting "€260k–€300k" when those are three
  margin choices around one point estimate is worse than presenting the point: it looks like
  uncertainty has been quantified when it has not.
- **Two different uncertainties, never merged.** *Execution* variance ("how long does this task
  take, given the scope as defined") is what three-point estimation measures, and it is handled
  with contingency days. *Scope* variance ("is the task what we think it is") is what the
  assumptions measure, and it is handled with assumptions and exclusions in the contract — never
  with days. On a decomposed professional-services scope the second is routinely several times
  the first, and merging them hides that.
- **Cost first, price second.** A price chosen for the win and back-filled with effort is how a
  team gets committed to work nobody sized. Build the cost, publish the options, let the decision
  be taken with its consequences visible.
- **Contingency is derived, not itemised by hand.** It is P80 − P50 (Step 7). A hand-picked set
  of risk lines is a guess wearing a table, and a flat 15% is a number nobody can defend.
- **The client's effort is part of the estimate.** Our days are not the only input the plan
  depends on, and their hours are the dependency most likely to be missing.

## Step 1 — basis of estimate

What the estimate covers and what it assumes, written before any number. It is what makes the
estimate re-baselineable when scope moves — and scope always moves.

- **Scope baseline:** the S-ID list and the version/date of `rfp_analysis.md` it came from.
- **Volumetric baseline:** the counts effort multiplies by, each cited. Uncited → `[⚠VERIFY]`.
- **Assumptions:** each one load-bearing — it changes a number if wrong. Copy the depth
  assumptions from the unbounded-language table verbatim; an assumption that lives only in the
  estimate and never reaches the bid is not a defence.
- **Exclusions:** what the price does not buy. On a fixed price this is the whole defence.
- **Constraints:** term, mandated milestones, named-personnel lock-in, site/clearance rules,
  client blackout periods.

## Step 2 — pick two techniques, and make them actually independent

Run **at least two techniques and reconcile the difference explicitly.** A single method has no
error bar; two that disagree by 40% have told you something before the client does.

| Technique | Use it when | Watch for |
|---|---|---|
| **Bottom-up (WBS)** | scope is decomposed — the default for professional services | omitted implied activities (mobilisation, governance, QA, review cycles, production) *and* the opposite failure: the same fieldwork counted under several work items — Step 3b |
| **Parametric** | the work scales on a countable driver — days per source system, per report, per interface | factors invented *after* the bottom-up, to match it |
| **Analogous** | a genuinely comparable prior engagement or bid exists | a prior *price* converted to days through **our own** rate and margin — see below |
| **Three-point / PERT** | an item's uncertainty is real, not decorative — `(O + 4M + P) / 6` | pessimistic values that are just the likely value plus a bit; P is what happens when the risk lands |

### Independence is a property of the process, not of the technique list

Two techniques run by the same person, in sequence, on the same afternoon are one technique run
twice. Anchoring is not defeated by relabelling. Three rules make the second estimate mean
something:

1. **Estimate the second way before comparing.** Write down the parametric factors, or the
   analogous number, and only then look at the bottom-up total. A factor set derived by dividing
   the bottom-up by the unit counts will always reproduce the bottom-up — and the resulting 4%
   agreement reads exactly like corroboration while carrying zero information.
2. **Draw the second estimate from a different data source.** Parametric factors from delivered
   engagements, not from this model. An analogous baseline from a prior *effort* record, not a
   prior *price*.
3. **Never launder an external number through your own model.** This is the one that hides best.
   A prior bid of €135k is the only genuinely independent datum available — converting it to days
   by dividing by *our assumed cost rate* and *our assumed margin* produces a number that agrees
   with our model **because it was computed from our model**. Test it: redo the conversion at two
   or three plausible external rates. If the verdict flips between "reconciles" and "does not",
   the check has no discriminating power and must be reported as inconclusive, not as a pass.

**Reconcile out loud.** State the gap in %, which estimate you are taking, and *why the other one
is wrong* — not merely that it differs. "Parametric is lower because it has no line for the
continuity strategy" is a reconciliation; "we take the bottom-up" is a preference.

### The outside view

The three techniques above are all *inside* views: they build the number from this engagement's
parts, and every one of them inherits this engagement's optimism. The countermeasure is a
**reference class** — what did engagements *of this kind* actually take, regardless of how this
one is decomposed?

- Best source: the firm's own delivered engagements of the same shape, by actual recorded days.
  If that dataset does not exist, **say so** — an outside view built from judgement is still worth
  having, but it must be labelled as judgement, not presented as a benchmark.
- Compare the bottom-up P50 against the reference band. **Landing outside it is not a reason to
  edit the number down** — it is a reason to find the mechanism. Either there is a real
  scope-specific cause (a genuinely doubled scope, a mandated deliverable set), or there is
  padding or double-counting (Step 3b). Report which, with the days attached.

## Step 3 — the effort model

Role × grade × days, per S-ID, phased across the term. Three views of the same numbers, because
three different people check three different things:

1. **By scope item** — does every S-ID have effort, and does the split look sane against the drivers?
2. **By phase** — does the shape match how this work actually runs, and does it fit the term?
3. **By grade** — is the pyramid deliverable *and* affordable *and* scoreable against a Personnel
   criterion? An all-senior model prices itself out; a junior-heavy one fails the CV section it
   is being marked on.

Grades and rates come from the firm's rate card. If it is not indexed in
`01_pursuit/_shared/firm_assets.md`, that is a materials-needed item — invented rates are the
fastest way to a margin that does not exist.

## Step 3b — the overlap audit

**This is the step that decides whether the number is inflated, and it is the one everybody
skips.** A scope decomposition is built to be *complete* — every clause covered, nothing missed.
Nothing in that construction stops two S-IDs from describing the same work seen from two angles,
and a bottom-up estimate then charges for both. Omission gets caught (the client notices);
duplication does not (the client just pays, or we lose the bid).

It bites hardest exactly where the decomposition is good, because a buyer's scope prose repeats
itself: a "review of the four data layers" and an "assessment of the warehouse, the ETL and the
reporting estate" are frequently the same interviews, the same documents and the same analysis
under two headings.

Go through every pair that shares an input and ask: **does the second item re-use the first
item's fieldwork?** Four recurring patterns:

| Pattern | What it looks like | Correct treatment |
|---|---|---|
| **Re-framing** | The buyer's scope states the same estate twice under different taxonomies (by layer, and by component) | One item carries the fieldwork; the other carries only the cross-cutting synthesis |
| **Synthesis charged as fieldwork** | "Assess against the client's N stated problems" after the workstreams have already assessed them | Mapping + write-up only — usually a third of the naive figure |
| **Downstream inheritance** | "Recommend a target architecture" after three options have been fully built and costed | Scoring and rationale, not a fresh design |
| **Threads booked as workstreams** | Security, continuity, sustainability — real content, but delivered *inside* other deliverables | Incremental effort only, not a standalone allocation |

Record it as a table — original days, revised days, and the reason — and keep it in the artefact.
A reviewer's first question about any estimate is "is this padded"; the audit is the answer, and
an estimate that shows its own deductions is far easier to trust than one that merely asserts a
total. **Also record what you looked at and did *not* cut** — an audit that only ever reduces is
a discount exercise, not an audit.

The counterpart check is Step 3's completeness sweep (mobilisation, governance, QA, review cycles).
Run both: bottom-up estimates fail in both directions, and the same read catches each.

## Step 4 — client-side effort

Estimate **their** hours too: role/group, activity, hours, and when in the term. Two reasons, and
both bite:

- Buyers increasingly require it in the response — a stakeholder-input table is a scored element
  in its own right, and it is one of the few places a bid can demonstrate it has actually
  planned rather than described.
- It is the biggest hidden dependency on any fixed price. A workshop costs us one facilitator-day
  and costs them eight attendee-hours; if those hours don't materialise, the term slips and the
  slip is ours. Quantifying the ask converts a silent dependency into a stated one — which is
  scope protection in the only form a buyer accepts: their own number, agreed up front.

## Step 5 — the range: two uncertainties, kept apart

The primary output of an estimate is a **distribution**, not a number. Two distributions, in fact,
and merging them is the most common way an estimate misleads its reader.

### 5a. Execution variance — P50 and P80

From the three-point figures: `mean = (O + 4M + P)/6`, `σᵢ = (P − O)/6` per item. Then the
**correlation assumption, which must be stated, because it dominates the answer**:

| Assumption | Aggregate σ | When it applies |
|---|---|---|
| Independent | `√Σσᵢ²` | items estimated separately, by different people, on unrelated work |
| **Partially correlated (ρ≈0.5)** | between the two | **the professional-services default** |
| Fully correlated | `Σσᵢ` | every item hangs on the same handful of assumptions |

Textbook PERT sums variances in quadrature — which assumes independence. On a decomposed
consulting scope that assumption is simply false: the line items share the same depth
assumptions, the same team, the same reading of the buyer's ask, so when one is wrong six are
wrong together. Applied blindly it collapses a 17-line estimate to a **±2% band**, which then sits
in the same document as the words "medium confidence". If a σ comes out implausibly tight, the
correlation assumption is the bug — not the estimate.

Report **P50** (the planning number) and **P80** (the commitment number), and say which
correlation assumption produced them.

### 5b. Scope variance — the assumption scenarios

Every load-bearing assumption from Step 1 carries a day impact if it is wrong. Sum the upside
exposure. **This is a different quantity from 5a and must be presented separately**: 5a asks "how
long will this work take", 5b asks "is this the work".

On a bounded, well-decomposed scope the scope band is routinely **several times** the execution
band. That finding is the single most useful thing the estimate produces, because the two are
managed by completely different instruments:

- execution variance → **contingency days** (Step 7), carried in the price
- scope variance → **assumptions and exclusions in the contract**, carried in the words

Pricing scope variance as contingency makes the bid uncompetitive and still does not protect it;
defending execution variance with an assumption clause leaves the team short of days. Say which
band each risk falls in.

## Step 6 — calibration, including the outside view

The checks that catch a wrong number while it is still cheap:

- **Overlap audit** (Step 3b) — the first thing a reviewer will probe.
- **Outside view** (Step 2) — P50 against the reference class, with the mechanism for any gap.
- **Implied FTE vs term.** Total days ÷ working days in the term = sustained FTE. Compare against
  the team we are actually naming and their availability. This is the check that catches the
  estimate nobody can staff.
- **Phase shape.** Does the effort split resemble this kind of engagement, or is 90% of it in a
  "synthesis" phase nobody has planned?
- **Grade pyramid.** Cross-check against the Personnel criterion and the blended rate.
- **Days per deliverable.** Against the buyer's own deliverable list. A board-ready target
  architecture at four days is not a target architecture.
- **Reconciliation** (Step 2) — the gap in %, which estimate we take, and why the other is wrong.
  An unreconciled gap is the estimate's largest undocumented risk.

## Step 7 — contingency = P80 − P50

Contingency is **derived from the distribution**, not assembled by hand: it is the execution-variance
gap from Step 5a. Hand-picking risk lines and adding them up double-counts whatever the three-point
spread already captured, and it produces a figure that cannot be defended as anything but taste.

Then handle separately the exposures that are **not** execution variance:

- **Scope-variance exposures** (Step 5b) — disposition is *excluded by assumption A-n*, with the
  assumption written into the response. Not days.
- **Cost items that are certain but not effort** — financing cost where payment is back-loaded to
  a completion milestone (we fund the engagement), non-labour, production. These are cost lines,
  not contingency: they are not uncertain, they are simply owed.
- **Exposures consciously accepted** — named, with the reason, so the acceptance is a decision
  rather than an omission.

State the total **excluded** exposure explicitly. That figure is what the partner is accepting
when they sign a fixed price, and it should never be discovered after signature.

## Step 8 — cost → price

In this order, every time — and stop at the cost base:

```
labour at P50 (Step 3)  +  non-labour (travel, licences, third parties, production)
                        +  financing / certain-but-not-effort cost (Step 7)
                        =  COST BASE at P50
                        +  contingency = P80 − P50 (Step 7)
                        =  COST BASE at P80
                        →  margin is a DECISION, taken by the partner (Step 9)
```

Publish both cost bases. Which one the price is built on is itself the first commercial choice,
and it should be visible rather than baked in.

Then model what the price has to survive: withholding taxes affect **cash flow**, not margin —
show both and don't conflate them. An extension option needs a rate card that protects the later
margin, not just this one. If the price the market will bear sits below the cost base, that is a
go/no-go input, not a rounding exercise — and it is the one finding an estimate must never soften.

## Step 9 — price vs score: decision support, not a recommendation

Where the buyer publishes the cost formula, **compute it**. `marks = (lowest ÷ ours) × max` is
non-linear, so the marginal cost of a euro is worth knowing exactly rather than feeling. Cap the
ratio at 1 — below the lowest bid you score full marks, you do not score more than full marks.

Then lay out the candidate prices as a **decision table**: price · resulting marks under two or
three assumed lowest bids · margin · what the foregone marks would have to be recovered from on
the quality side. State the assumed competitor range as the guess it is.

**Stop there.** Do not name a recommended bid price. The price decision weighs client appetite,
competitive intelligence, portfolio position and risk tolerance that this model does not contain
and the estimator does not own. Presenting a recommendation invites the reader to accept the
number rather than interrogate it — and the reader is precisely the person whose judgement the
firm is relying on. Give them the tradeoff fully worked, and the observations that only the model
can supply ("below €X we are under cost base"; "€11k of margin costs 10 marks"), then let them
decide.

## Step 10 — into the buyer's pricing document

Map our model onto **their** format, and respect it exactly. Format non-compliance on pricing is
a common auto-reject: a single lump-sum cell means a single lump-sum cell, however much we would
like to show the breakdown. Record which of our numbers goes in which cell, what must be
suppressed, and where the breakdown *is* allowed to appear (usually the methodology narrative,
sometimes nowhere).

Check the arithmetic against every place the price is restated — the form of tender, the pricing
workbook, the cover letter. A price that disagrees with itself across two documents is the
cheapest possible way to lose.

## Step 11 — re-baseline triggers

**Say where on the cone of uncertainty this estimate sits.** A pre-award estimate built on a
scope decomposed from tender prose, with three unpublished volumetrics, is not the same animal as
one built after two weeks of discovery — and the honest accuracy band differs by a factor of
several. Naming the stage tells the reader how much to trust the decimal places, and it is the
difference between a range that narrows as evidence arrives and one that is quietly treated as
final because nobody said otherwise.

Then name the events that force a **rebuild** rather than an adjustment:

- a clarification answer that widens or bounds scope
- a volumetric that turns out wrong
- a mandated deliverable or milestone appearing in an addendum
- the named team changing
- the analogous baseline turning out not to be comparable

Each trigger is a pointer back to Step 1: the basis of estimate is what makes a rebuild a
half-day rather than a restart.

## The artefact: one workbook, and a generated snapshot

An estimate that only exists as prose cannot be reviewed properly. Changing one line item from 20
days to 26 means recomputing the total, the PERT mean, sigma, P50, P80, contingency, labour cost,
two cost bases and every margin and mark figure downstream — by hand, in a document that does not
recalculate. That is where arithmetic drift enters, and it denies the reviewer the one thing they
most want to do: move an input and see the consequence.

But shipping a spreadsheet *and* a hand-written narrative is worse: two things to keep in step,
and nothing keeping them there. **The workbook is the single maintained artefact.** It carries the
numbers as formulas and the judgement on its own sheets — basis of estimate, techniques and their
reconciliation, the outside view, calibration, contingency, the pricing-document mapping,
re-baseline triggers. Prose belongs in a wrapped cell, not in a second file.

```
workbook (maintained)  ──  export  ─►  markdown snapshot (generated, read-only)
```

**The markdown snapshot is generated, never edited.** It exists for two things a binary cannot
do: the mechanical gates read text, so an xlsx-only estimate falls out of every lint rule; and
`git diff` on a workbook shows nothing, which matters on a bid that gets re-priced three times.
Regenerate it after each round of edits and let it carry a DO-NOT-EDIT banner, so nobody spends
an afternoon improving a file that the next export overwrites.

**Seeding runs once, and re-seeding is destructive.** The markdown template is a convenient way to
draft the first version; after that the direction reverses. A tool that rebuilds the workbook from
the markdown on every run will silently discard the reviewer's edits — which is exactly the bug
this pack shipped and had to fix.

**The rate card is one table.** Rates typed inline against each grade mean that the day the real
card lands you edit every row and hope you caught them all. Put them in one place and have the
grade rows look them up. It also tends to be a deliverable in its own right — many tenders require
a rate schedule for extension or call-off work — and that schedule should not be maintained twice.

**A rate you cannot source is 0, not a guess.** Placeholder rates that look plausible get quoted;
zeros do not. Carry an explicit status flag on the card and have the cost sheet refuse to present
itself as committable until it reads `ACTUAL`.

**Guard every division.** A model whose rate card is empty, or whose scope table is not filled in
yet, must return zeros — not `#DIV/0!` spreading across nineteen sheets. A half-built estimate
should still open and still be legible.
