---
name: eng-estimate
description: Use when a tender, proposal, SOW or change request has to be sized or priced, or an existing estimate workbook needs updating, recalculating, or refreshing — "how many days is this", "size the engagement", "build the effort model", "what should we bid", "price the RFP", "estimate this scope", "update the rate card", "refresh the estimate", "fill the pricing document". Produces and maintains a formula-live Excel effort model traced to the scope decomposition, an overlap audit, a P50/P80 range separated from scope-variance scenarios, the client-side hours ask, a genuinely independent cross-check plus an outside view, a cost→price build, and the price-vs-marks decision table. Decision support for the pricing call — it does not recommend a bid price.
---

# Estimating an engagement

Turn a decomposed scope into effort, effort into cost, and cost into a price posture — bottom-up,
cited, cross-checked, with a stated error bar.
Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/estimation.md`.

## Prerequisite — the scope decomposition

`rfp_analysis.md` §3 must hold the S-ID table with **effort drivers** (the countable thing each
item scales on) and the volumetric baseline.

**If missing:** stop and run `eng-rfp-analyze` step 2b first. Estimating from RFP prose means
estimating the same sentence three different ways on three different days — and the number that
survives is whichever one was written down last. Building the scope table takes less time than
reconciling three guesses.

Also read before starting: `bid_reuse_analysis.md` if it exists (a prior lump sum is the cheapest
sanity check available) and `01_pursuit/_shared/firm_assets.md` for the rate card.

**One maintained artefact: the workbook.** `estimation.xlsx` holds the numbers as live formulas
*and* the judgement — basis of estimate, techniques and their reconciliation, the outside view,
calibration, contingency, the pricing-document mapping, re-baseline triggers — each on its own
sheet. `estimation.md` is a **generated snapshot**, never edited by hand.

**Fourteen sheets, none of them filler.** The judgement — basis of estimate, techniques, outside
view, phasing, calibration, contingency, pricing-document mapping, re-baseline triggers — is one
row per topic on the `Judgement` sheet, with a state column that says `OWED` and a footer that
counts what is unwritten. As eight separate tabs this was a third of the workbook holding four
words each, and an empty tab named `BasisOfEstimate` made a missing basis of estimate look present.

```
workbook (source of truth)  ──  eng-estimate refresh  ─►  markdown snapshot (generated, read-only)
```

## Conversation contract

Prefer the plugin skill's explicit invocation, `/engagement-os:eng-estimate`. Also treat
natural-language requests such as “size this tender”, “create the estimate workbook”, “change the
Manager rate to €x”, “re-run the estimate”, “sync the snapshot”, or “show what moved since the
last price” as fallback invocations of this skill.

- Never ask the user to run Python, a script, or a CLI flag.
- Never ask the user to edit `estimation.md`.
- Accept changes in conversation and write them to `estimation.xlsx`; if the user prefers to edit
  the workbook directly, read those edits back.
- After every workbook change, recalculate, verify zero formula errors, and overwrite the generated
  `estimation.md` snapshot. Return the workbook path, the snapshot path, and the material deltas.
- Then invoke `Skill(engagement-os:eng-propagate-change)`: a changed cost, duration, assumption,
  exclusion or client-time ask invalidates the analysis headline and every response section
  declaring or containing that pricing dependency. Do not checkpoint until those hand-offs and
  any required human re-review are complete.
- Preserve prior versions through git history during working changes. At a formal pricing freeze,
  copy both artefacts into `4_final/`; do not create dated working snapshots.

## Agent-only implementation

The deterministic engine is
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/build_estimate_workbook.py`. It is an implementation
detail behind this skill, not a user entry point. Seed once from
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/estimation.md.tmpl`; thereafter export from the
workbook to the snapshot. Run the engine yourself and translate its result into plain language.
Only explain its CLI when the user explicitly asks about implementation.

**Re-seeding is destructive and the engine refuses it by default.** It used to rebuild from the
markdown on every run, so a reviewer's workbook edits vanished on the next build while the docs
told them the workbook was the model. Never discard workbook edits unless the user explicitly
asks to rebuild from the snapshot and acknowledges that those edits will be lost.

**Why keep a markdown snapshot at all** when the workbook is the source: `eng_lint` reads text,
so an xlsx-only estimate falls out of every mechanical gate; and `git diff` on a binary shows
nothing, which matters on a bid re-priced three times. The snapshot is regenerated after each
edit and carries a DO-NOT-EDIT banner.

**Invoke the installed `xlsx` skill through the Skill tool before any workbook mutation or
verification (`Skill(xlsx)`, or `Skill(document-skills:xlsx)` if that is how it is installed
here — a companion skill is invoked bare when it is a personal skill and namespaced under
its plugin when it came from one; `eng-check companions` prints this machine's name for it).** Use it for anything spreadsheet-shaped beyond running this
engine — editing the workbook, adding a sheet, changing formatting, or diagnosing a formula. It owns the
conventions this workbook already follows (Arial; blue text for inputs, black for formulas, green
for cross-sheet links, yellow fill for cells to edit; percentages stored as fractions) and the
function-compatibility rules that decide whether a formula survives verification. Do not re-derive
any of that here.

**Recalculation is mandatory and belongs to the `xlsx` skill.** openpyxl writes formulas with no
cached values, so an un-recalculated workbook reads back empty to every previewer — and a function
LibreOffice cannot evaluate bakes a literal `#NAME?` into what we hand the client. The builder
calls the skill's `scripts/recalc.py` automatically and exits non-zero if it reports errors; if it
cannot find the skill it says so and stops rather than guessing. **Never substitute
`soffice --convert-to`** — it converts the file and reports no formula errors at all, which looks
like verification and is not. (Found the hard way: it passed a workbook that recalc.py then failed
on a real `#N/A`.)

The tables the script reads carry an explicit `<!--table:KIND-->` marker — **keep the marker
directly above its table and keep the column order**. The script reports how many rows it took
per table, so a marker that has drifted away from its table shows up as `0 row(s)` rather than
as a quietly wrong total.

**The rate card is one table, in one place** (`RateCard` sheet, `<!--table:ratecard-->` in the
markdown). Grades look rates up from it, so replacing a placeholder card with the firm's real one
re-costs the whole model without touching another cell. Until its status cell reads `ACTUAL`, the
workbook stamps "PLACEHOLDER RATES — this cost base is not committable" on the Cost sheet. Rates
you cannot source go in as **0**, not as an invention: a visible zero is a better wrong answer
than a plausible one.
On the delivery side the same skill sizes a change request or a phase 2 — only the scope input
changes (SOW items instead of S-IDs); write it next to the artefact it prices.

## Workflow

```
Estimation Progress:
- [ ] 1. Basis of estimate — volumetrics, assumptions, exclusions, constraints
- [ ] 2. Second technique FIRST, from a different data source — then reconcile out loud
- [ ] 2b. Outside view — reference class; if no dataset exists, label it judgement
- [ ] 3. Effort model: S-ID × activity × role/grade × days, three-point where uncertain
- [ ] 3b. OVERLAP AUDIT — which items re-use another item's fieldwork (+ what you kept)
- [ ] 3c. SCHEDULE — duration, dependencies, staffing, from the SAME S-IDs the cost uses.
        Duration = effort ÷ (people × working days × utilisation), so a discrete activity's
        duration is derived and a level-of-effort line (governance, QA, review cycles) takes its
        span from the term with the staffing derived instead. Three checks: every estimated day
        is scheduled · the schedule fits the term · **peak** weekly FTE (not the average) is
        staffable. A cost base with no schedule cannot say when anything lands or who is free
- [ ] 4. Client-side effort — their hours, by group, by week
- [ ] 5. Range: P50/P80 with a STATED correlation assumption, kept apart from scope scenarios
- [ ] 6. Calibration: overlap · outside view · implied FTE · phase shape · pyramid · days/deliverable
- [ ] 7. Contingency = P80 − P50; scope exposure excluded by assumption, stated as a total
- [ ] 8. Cost base at P50 and at P80 — stop there, margin is not ours to set
- [ ] 9. Price-vs-marks DECISION TABLE — no recommended price
- [ ] 10. Map onto the buyer's pricing document, obeying its format exactly
- [ ] 11. Cone-of-uncertainty stage + re-baseline triggers
- [ ] 12. Create/update the workbook, recalculate through `xlsx`, refresh the snapshot, and check row counts.
         An EXISTING workbook gains sheets a newer builder knows about through the upgrade path —
         never by re-seeding, which discards the model. And never seed from `estimation.md`: it is
         the generated snapshot, has no table markers, and seeding from it yields a workbook of
         placeholder rows (the builder now refuses)
```

**Step 2 — independence is a property of the process.** Two techniques run by the same person in
sequence are one technique run twice. Write the second estimate down *before* looking at the
bottom-up total, and draw it from a different data source. Above all, **never convert an external
number through your own model**: dividing a prior bid's price by your own cost rate and your own
assumed margin produces agreement by construction. Test any analogous check at two or three
plausible external rates — if the verdict flips, report it as inconclusive, not as a pass.

**Step 3 — bottom-up fails in both directions.** Under-count: the activities the RFP never
mentions still consume days — mobilisation, governance, QA, document production, client review
cycles, rework. Over-count: see 3b.

**Step 3b — the overlap audit, and the one everybody skips.** A scope decomposition is built for
completeness, and nothing in that construction stops two S-IDs describing the same work from two
angles. Omission gets caught by the client; duplication just gets paid for, or loses the bid.
Ask of every pair sharing an input: *does the second re-use the first's fieldwork?* The four
recurring patterns — re-framing, synthesis charged as fieldwork, downstream inheritance, threads
booked as workstreams — are in the method file. Show the deductions **and** what you examined and
kept; an audit that only ever cuts is a discount, not an audit.

**Step 4 — estimate their effort too.** A workshop costs us one facilitator-day and costs them
eight attendee-hours. Some RFPs score a stakeholder-input table outright; on a fixed price it is
the biggest hidden dependency either way, and quantifying it is the only scope protection a buyer
accepts — their own number, agreed up front.

**Step 5 — the correlation assumption dominates the answer, so state it.** Textbook PERT sums
variances in quadrature, which assumes the line items are independent. On a decomposed consulting
scope they are not: they share the same depth assumptions and the same team, so when one is wrong
six are wrong together. Applied blindly it can collapse a 17-line estimate to a ±2% band sitting
next to the words "medium confidence". Default to partial correlation and **say so**. If σ comes
out implausibly tight, the correlation assumption is the bug.

And keep the two uncertainties apart: **execution** variance (P80 − P50, handled with contingency
days) versus **scope** variance (the assumption scenarios, handled with assumptions and exclusions
in the contract). The second is routinely several times the first — which is the most decision-useful
thing the estimate produces, and it disappears the moment they are merged.

**Step 9 — compute the formula, then stop.** Where the buyer publishes `marks = lowest ÷ ours ×
max` (cap the ratio at 1), price converts to marks arithmetically. Build the decision table and
state the assumed competitor range as the guess it is.

## Guardrails (the doctrine)
- **The estimate informs the price; it does not set it.** Pricing weighs client appetite,
  competitive position and risk tolerance that this model does not contain. Produce the range,
  the drivers and the tradeoff — **never a "recommended bid price"**. The partner decides; a
  recommendation invites them to accept the number instead of interrogating it.
- **Every effort line traces to an S-ID.** No S-ID → the scope table is incomplete, go back. An
  S-ID with no effort line → we have quietly agreed to do something for free.
- **Rates are claims too.** A day rate, productivity factor or benchmark that can't be sourced to
  the rate card, an indexed asset, or a cited reference is `[⚠VERIFY]` — not a number.
- **A price band is not a range.** Three margin choices around one point estimate is not
  quantified uncertainty; presenting it as one is worse than presenting the point.
- **Contingency is derived, not hand-picked.** P80 − P50. Adding up chosen risk lines
  double-counts whatever the three-point spread already caught.
- **Assumptions must reach the bid.** One that lives only in `estimation.md` defends nothing —
  scope variance is carried by contract words, not by days.

## Hand-off
Return the range, assumptions, exclusions, client-time table, P50/P80, and decision table to the
`rfp-arrived` playbook. It updates `rfp_analysis.md` §10 and uses the cost base in commercial and
delivery decisions. Do **not** invoke drafting from this skill; the playbook owns sequencing and
passes the pricing material to `Skill(engagement-os:eng-bid-respond)`. Once the partner takes the pricing
decision, record it in `_pm/raid_and_decisions.md`, not back into this file.
