---
name: eng-bid-research
description: Use when a bid analysis has surfaced gaps to close or win-themes to arm with proof, or the user says "research this for the bid", "find evidence for X", "what can we cite for the tender", or after eng-rfp-analyze produces a materials-needed list. Comprehensive (depth AND breadth), evidence-based research — every claim carries a citation a reviewer can open; distinguishes external research [T3:OWN] from firm-held uploaded materials; nothing fabricated, and anything unsourceable is marked [⚠VERIFY] and kept out of the bid.
---

# Researching for a bid

Close the gaps a bid analysis surfaced with research that is comprehensive, evidence-based, and
zero-fabrication — so every claim reaching the response can be walked back to a real source.
Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-research.md`.

## Driven by the analysis
Research is scoped by the **materials-needed list** and every `gap` in `compliance_matrix.md`
(from `eng-rfp-analyze`). Don't research at large — research to close named gaps and arm the
high-weight win-themes. Each task names the Req ID / theme it serves. Log findings in
`2_analysis/bid_research_log.md` (template in `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`).

**If missing:** no compliance matrix / materials-needed list →
`Skill(engagement-os:eng-rfp-analyze)` first.
Without the gap list there is no scope to research against; an unscoped "general pass" produces
plausible-looking findings nobody asked for — the worst failure mode under zero-fabrication.

Unless this skill was invoked by the change-propagation hand-off itself, first invoke
`Skill(engagement-os:eng-propagate-change)`. A manually changed matrix row can alter which gaps
need research; continuing from the previous list would research the wrong scope.

## Workflow

```
Bid Research Progress:
- [ ] 1. List every gap / needed item from the analysis (breadth = cover them all)
- [ ] 2. External stream: web/standards/market/competitor → [T3:OWN], each with a URL/locator
- [ ] 3. Internal stream: firm-held case studies / CVs / past bids the user uploads → cite the doc
- [ ] 4. Each claim: primary-over-secondary, dated, one solid cited fact beats three vague ones
- [ ] 5. Anything unsourceable → [⚠VERIFY] with what would close it (do NOT let it become a claim)
- [ ] 6. Log every finding: serves / claim / stream / source+locator / tag / confidence / status
```

**Breadth AND depth.** Breadth = no flagged gap left dark (a bid loses on the un-researched
requirement). Depth = each grounded in a real, cited source. Work each gap to a `closed` row or an
explicit `[⚠VERIFY]`.

**Two streams, kept separate.** External (`[T3:OWN]`) = our research of the outside world (web,
standards, benchmarks). Internal = firm-held materials the user uploads (case studies, named-staff
CVs, past-bid text, certs, referees, pricing). If a win rests on an internal figure, ask the user
to confirm it.

## Guardrails (the zero-error gate)
- No number, credential, or outcome enters the response without a `closed` log row + citation.
- When sources disagree, keep both and apply precedence — never average or guess.
- Fact (cited) vs inference (hedged, marked) — never let an inference read as fact.
- Fabricating or "rounding up" a credential/metric/reference is an automatic disqualifier.

## Hand-off
Once the human GO gate has passed, the closed research log →
`Skill(engagement-os:eng-bid-respond)`. Open `[⚠VERIFY]` rows are closed or cut before the
response asserts them.
