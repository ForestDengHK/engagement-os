# RFP / bid analysis method

How to decompose a tender into a scored, traceable analysis that drives a winning, compliant
response — aligned twice (to the RFP text AND to our best practice), read from every role's
angle, and honest about what we don't yet have.

## Contents
- Where analysis sits in the pursuit pipeline
- The zero-error, dual-alignment doctrine
- Step 1 — requirement extraction (every requirement gets an ID + clause cite)
- Step 2 — the compliance / response matrix
- Step 2b — scope decomposition (the estimation baseline)
- Step 2c — our understanding & our solution (does it actually solve their problem?)
- Step 3 — evaluation criteria & weights map (score-driven)
- Step 4 — multi-role analysis (the panel lens)
- Step 5 — win-themes & differentiators (evidence, not slogans)
- Step 6 — risks, red-flags, deal-breakers
- Step 6b — clarification questions (derived by dimension sweep, panel lens, human sends)
- Step 7 — materials-needed list (research vs upload)
- Step 7b — prior-bid check (conditional, and the negative result is recorded)
- Step 8 — proceeding assumptions & escalations

## Where analysis sits in the pursuit pipeline

```
RFP arrives ─► ingest (eng-ingest-source → 01_pursuit/<ENG-ID>/1_received/_md)
           ─► ANALYSE (eng-rfp-analyze → 2_analysis)   ← this file
           ─► research gaps (eng-bid-research)
           ─► respond (eng-bid-respond → 3_drafting → 4_final)  ─► panel red-team gate
```

The RFP is a **T-source of record** for pursuit, exactly as the system-of-record is for
delivery: every requirement, weight, and constraint is quoted from it and cited by clause.
Tag RFP-sourced facts `[RFP §x]`; our own research `[T3:OWN]`; anything unconfirmed `[⚠VERIFY]`.

## The zero-error, dual-alignment doctrine

A bid with one wrong or unsourced claim loses trust — and the tender. So:

- **Nothing fabricated.** Every capability, credential, metric, or reference we assert must
  trace to a real source (a past project, a CV, a case study, a cited standard). If we can't
  source it, it does not go in the bid — it becomes a `materials-needed` item or an `[⚠VERIFY]`.
- **Dual alignment.** Every response line aligns to (a) the specific RFP requirement it answers
  and (b) our methodology / best practice. A generic best-practice answer that doesn't map to a
  requirement is noise; a requirement answered off-method is a liability.
- **Traceable both ways.** From any requirement you can find our response; from any claim in the
  response you can find its RFP requirement and its evidence.

## Step 1 — requirement extraction

Read the whole RFP (and every appendix/schedule) via the ingested markdown. Inventory every
obligation-bearing source unit in `requirement_coverage.md`: numbered clause/question, form table,
schedule, submission instruction and unnumbered mandatory text. Extract **every**
obligation, not just the obvious ones — scope items, mandatory qualifications, submission
mechanics, format rules, deadlines, evaluation weights, contract terms. Give each a stable
**Req ID** and cite the exact clause. Mandatory ("must/shall") vs
desirable ("should/may") is a required flag — mandatories are pass/fail gates.

Reconcile both ways: every source unit has a reasoned disposition and every Req ID appears in a
mapped row. An internally complete matrix can still be a perfectly organised subset of the RFP.

**Citation order: the document's own numbering first.** If the RFP numbers its clauses
(`§2.1(f)`, `§5.1.3`, Appendix 5 clause 16), cite those — they are stable, checkable by the
buyer, and survive re-pagination. The converted markdown's `## Page N:` anchors are the
fallback for documents with no native numbering, not the default: pandoc-style headings are
not guaranteed stable across converters, and "page 12" rots the moment the buyer issues an
amended PDF.

## Step 2 — the compliance / response matrix

The centrepiece artefact (`compliance_matrix.md`). One row per requirement:

`Req ID | RFP clause (§) | Requirement | Mandatory? | Response / control | Proof required? | Proof source / status | Owner | Gap type | Status`

Rules: every requirement has a row; every mandatory row must reach `met`. Separate knowing how to
answer from holding proof. `Proof required? = no` needs an explicit control reason; otherwise a
missing proof source is a proof gap. Gap type is none / answer / proof / control / clarification.
The matrix closes the response; the coverage audit proves the source was completely considered.

## Step 2b — scope decomposition (the estimation baseline)

The compliance matrix answers *"did we address everything they asked for?"*. It does not answer
*"how big is this?"* — a row reading "the vendor shall conduct a comprehensive assessment of the
Data Warehouse and application landscape" is one requirement and six weeks of work. **Without a
scope decomposition there is no estimate, and without an estimate the price is a guess dressed
as a lump sum.**

Break the buyer's scope prose into numbered work items (`S-01…`), each with its clause, the
deliverable it feeds, and — the part everyone skips — **the effort driver**: the countable thing
the work scales on. "Assess the source systems" costs what it costs because there are 5 of them
and 18 loads between them; the number is in the RFP and belongs in the analysis, not rediscovered
in the pricing spreadsheet a week later.

- **Volumetric baseline.** Every count the effort model will multiply by, cited. Servers, source
  systems, interfaces, reports, universes, stakeholder groups, sites, environments, data domains.
  An uncited count is `[⚠VERIFY]` and usually a clarification question.
- **Explicitly out of scope.** Say it back to them. On a fixed price this is the only thing
  standing between the estimate and everything the buyer assumed was included.
- **Unbounded language.** "Comprehensive", "as required", "including but not limited to", "the
  application landscape" — each has no natural stopping point. Every one gets either a
  clarification question or a **stated depth assumption** that carries verbatim into both the
  estimate and the response. An assumption stated in the estimate but not in the bid is not a
  defence.
- **Acceptance.** What must be shown, and who signs. On a completion-triggered payment this
  decides when we get paid, so it is scope, not admin.
- **Scope items the RFP implies but never states** — mobilisation, governance/steering, QA,
  document production, client review cycles. They consume real days and appear in no clause.
  Record them as scope items marked *implied*, or they are absorbed out of margin.

Hand this table to `eng-estimate`. An S-ID with no effort driver is not estimable — fix it here,
not by padding later.

## Step 2c — our understanding & our solution

Two failures this step exists to prevent, and both are common enough that evaluators score for
them explicitly:

1. **Restating the buyer's words back as "understanding".** If our understanding section says
   nothing the RFP does not already say, we have demonstrated reading comprehension, not insight.
   The test: does it name a cause, a consequence, or a connection the buyer did not write down?
2. **A method with no target.** A phased approach that never names which client challenge each
   phase resolves is a framework dump. The buyer's own limitations list is the checklist —
   answer it item by item.

One row per client challenge: their statement (cited) → what we think is actually driving it →
what we would do → **does that resolve it: fully / partly / no** → the named standard or
reference architecture it conforms to → the asset that proves we can do it.

- **Name the standard.** "Industry best practice" is an opinion with a suit on. DAMA-DMBOK,
  TOGAF ADM, the Kimball model, the vendor's own well-architected framework, ISO 27001, NIS2 —
  something an evaluator can check. If no standard applies, say the reasoning is ours and own it.
- **Answer the "so does it work" question.** A solution row whose verdict is *partly* or *no* is
  more credible than five rows of *fully*, and it is the honest input to risk ownership. State
  what we propose instead — a phase 2, a client-side action, an explicit assumption.
- **Alignment is dual, per element** (the doctrine, made checkable): each solution element maps
  to (a) the requirement it answers, (b) the methodology or asset we run it with, (c) the standard
  it conforms to. Missing (b) is a capability asserted without a method — a delivery risk that
  becomes a red-team finding. Missing (c) is the opinion problem above.
- This section is the **source text for the response's method and deliverables sections**, which
  is usually where the marks are concentrated. Writing it in analysis rather than in drafting is
  what stops the response being invented under deadline.

## Step 3 — evaluation criteria & weights map

Bids are scored, so analysis is score-driven. Extract the evaluation criteria and their weights;
map each to the requirements and to where our response will earn the points. Identify the
**high-weight, high-differentiation** areas — that's where to concentrate win-themes and proof.
If weights aren't published, infer and mark `[⚠VERIFY]`.

**Extract the rubric, not just the weights.** Most tenders define what each score BAND means
("90–100% = exceptional evidence of capability" … "0–10% = failed to address the question"),
usually as an unnumbered table beside the evaluation section, not inside the weights table.
The rubric tells you the evidence density each band demands — it is the difference between
writing eloquently and writing to the evidence count. An analysis that maps weights but misses
the rubric has read how much each answer is worth and not what a full-marks answer looks like.

**Date sanity.** Every extracted date gets compared against the analysis date. A deadline in
the past is a red-flag row in §7 and the first clarification question (closed? extended?
re-issued?) — never a quietly-recorded fact. A team that discovers a closed tender at
submission has burned the engagement; this is the cheapest check in the whole method.

## Step 4 — multi-role analysis (the panel lens)

Read the RFP from multiple role perspectives (reuse the Panel Framework roles if installed;
otherwise walk the lenses manually). Each role surfaces what a single reader misses:

- **Client sponsor / evaluator's eye** — what will actually win the points; what the buyer fears.
- **Solution architect** — technical feasibility, the real shape of the solution, NFRs.
- **Engagement partner / commercial** — margin, pricing exposure, resourcing.
- **Legal / contracts** — onerous terms, liability caps, IP, indemnities (feeds Step 6).
- **Delivery lead** — can we actually staff and deliver this on the stated timeline?
- **Sector / domain SME** — domain-specific obligations, regulatory context.

Record each role's read against the requirements; conflicts between roles are recorded, not
smoothed (same discipline as findings).

## Step 5 — win-themes & differentiators

Derive 3–5 win-themes: the reasons *we* win this, expressed as buyer benefits and **backed by
evidence** (a named prior engagement, a measurable outcome, a credential). A win-theme without
proof is a slogan — cut it or send it to materials-needed. Map each theme to the high-weight
evaluation criteria from Step 3.

## Step 6 — risks, red-flags, deal-breakers

Flag: onerous / uncapped-liability terms, unpriceable or ambiguous scope, impossible timelines,
mandatory qualifications we may not meet, conflicts of interest, IP/data terms. Each risk gets an
owner and a mitigation or a clarification-question to submit to the buyer. Deal-breakers feed the
risk and proceeding-assumption register.

## Step 6b — clarification questions (derived, not noticed)

Questions to the buyer are **produced by a sweep, not collected as they occur to someone**. The
query deadline lands early and closes hard; after it, every remaining ambiguity can only be
handled by stating an assumption, which scores worse than an answer. Anything not asked in time
is a permanent loss, so the sweep runs as part of analysis — before drafting, not after.

**Sweep every dimension, one at a time.** Each has its own characteristic ambiguity, and a
free-form re-read finds the ones in whichever dimension the reader happens to think in.

| Dimension | What to interrogate | Typical ambiguity worth a question |
|---|---|---|
| **Scope & deliverables** | what is in, what is explicitly out, acceptance | "assessment of the estate" — which systems, to what depth, whose sign-off ends it |
| **Solution & architecture** | mandated platforms, constraints, integration surface | is the target platform a decision already taken or one we are asked to make |
| **Evidence & qualification** | recency rules, referee rules, staff-substitution rules | is "within 3 years" measured from project start or completion (decides whether an asset is in-window) |
| **Commercial & contract** | liability caps, payment triggers, IP, indexation, change mechanism | uncapped liability, or a milestone whose payment trigger is undefined |
| **Delivery & resourcing** | timelines, client-side availability, location, security clearance | a timeline that assumes client resources nobody has committed |
| **Evaluation & process** | scoring split, page limits, format rules, submission mechanics | whether page limits count appendices, whether CVs sit inside the section budget |

**Then run the multi-role lens over the question set** — `panel-discuss` if the Panel Framework
is installed (the legal, commercial, architecture and delivery roles each find ambiguities the
others read straight past), otherwise a manual pass through those four angles. This is the same
lens as Step 4 and for the same reason: a single reader's blind spots become the questions
nobody asked.

**Then the human reviews and sends.** The agent drafts the full question set with a recommended
wording and a stated consequence per question; the human decides what actually goes to the
buyer — some questions reveal more about our position than the answer is worth, and that call
is not the agent's.

Each question is logged in `clarification_log.md` with: the dimension, the clause it attaches
to, why it matters (what changes in our response depending on the answer), and — if unanswered —
the **settled reading** we will proceed on plus its consequence. Buyer answers are circulated to
all bidders and become part of the tender documents: they re-enter through the source loop and
move matrix rows like any other arrival.

## Step 7 — materials-needed list (research vs upload)

The explicit two-column ask, so nothing is silently assumed:

- **We research** (`→ eng-bid-research`): market/competitor context, standards, comparable
  outcomes, anything externally knowable.
- **You upload** (client/us): specific case studies, CVs of named staff, past-bid text we can
  reuse, pricing inputs, certifications, referee contacts — anything only the firm holds.

Be specific ("the 2024 utility DWH case study with the €X saving," not "a relevant case study").

## Step 7b — prior-bid check (conditional, and the negative result is recorded)

Most tenders are a variant of one already answered, so before drafting: **is there a prior bid?**
A re-issue, a follow-on, the same buyer asking again, or the same scope for a different buyer.
Search `01_pursuit/` and any `archive-*` tree, and ask the user — they may hold one the repo
doesn't.

The result is binary and both branches are explicit:

- **A prior bid exists** → convert it (`eng-ingest-source` → `01_pursuit/archive-<PRIOR-ID>/`) and
  fill `bid_reuse_analysis.md` — section by section, field-level diff. Do this *before* drafting.
- **No prior bid** → **do not create `bid_reuse_analysis.md`.** An empty or speculative reuse
  analysis is worse than none: it reads as done work, and the next reader trusts it. Record the
  negative in `rfp_analysis.md` §9 — *"searched X, none found"* — so it is visibly a checked
  fact rather than a forgotten step.

The same rule holds for any conditional artefact: **the file exists because the condition held,
never because the template list said so.** A scaffolder plants the artefacts every bid needs;
everything else is created on the evidence that it applies.

## Step 8 — proceeding assumptions & escalations

Material supplied to this workflow is treated as authorised GO. Synthesise the conditions the
team must manage: evidence, delivery, commercial, legal and timing. Give each an owner, consequence,
and explicit treatment in the estimate or response. Escalate facts; do not make or enforce the
team's bid/no-bid decision.
