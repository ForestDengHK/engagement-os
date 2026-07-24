# RFP / bid analysis method

How to decompose a tender into a scored, traceable analysis that drives a winning, compliant
response — aligned twice (to the RFP text AND to our best practice), read from every role's
angle, and honest about what we don't yet have.

## Contents
- Where analysis sits in the pursuit pipeline
- The zero-error, dual-alignment doctrine
- Step 1 — requirement extraction (every requirement gets an ID + clause cite)
- Step 2 — the compliance / response matrix
- Step 3 — evaluation criteria & weights map (score-driven)
- Step 4 — multi-role analysis (the panel lens)
- Step 5 — win-themes & differentiators (evidence, not slogans)
- Step 6 — risks, red-flags, deal-breakers
- Step 7 — materials-needed list (research vs upload)
- Step 8 — go / no-go recommendation

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

Read the whole RFP (and every appendix/schedule) via the ingested markdown. Extract **every**
obligation, not just the obvious ones — scope items, mandatory qualifications, submission
mechanics, format rules, deadlines, evaluation weights, contract terms. Give each a stable
**Req ID** and cite the exact clause (`§`, page, appendix). Mandatory ("must/shall") vs
desirable ("should/may") is a required flag — mandatories are pass/fail gates.

## Step 2 — the compliance / response matrix

The centrepiece artefact (`compliance_matrix.md`). One row per requirement:

`Req ID | RFP clause (§) | Requirement (verbatim/paraphrase) | Mandatory? | Our response approach | Evidence / proof | Owner | Gap? | Status`

Rules: every requirement has a row; every mandatory row must reach `met`; a row with no evidence
is a `gap` (→ materials-needed or research). The matrix is the completeness check — the response
is done when every row closes.

## Step 3 — evaluation criteria & weights map

Bids are scored, so analysis is score-driven. Extract the evaluation criteria and their weights;
map each to the requirements and to where our response will earn the points. Identify the
**high-weight, high-differentiation** areas — that's where to concentrate win-themes and proof.
If weights aren't published, infer and mark `[⚠VERIFY]`.

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
go/no-go.

## Step 7 — materials-needed list (research vs upload)

The explicit two-column ask, so nothing is silently assumed:

- **We research** (`→ eng-bid-research`): market/competitor context, standards, comparable
  outcomes, anything externally knowable.
- **You upload** (client/us): specific case studies, CVs of named staff, past-bid text we can
  reuse, pricing inputs, certifications, referee contacts — anything only the firm holds.

Be specific ("the 2024 utility DWH case study with the €X saving," not "a relevant case study").

## Step 8 — go / no-go recommendation

Synthesise: fit to our best practice, win probability given weights + differentiators, deliverability,
commercial attractiveness, and any deal-breakers. State a clear **go / no-go / go-if** with the
conditions. This is a recommendation with evidence, not a vote.
