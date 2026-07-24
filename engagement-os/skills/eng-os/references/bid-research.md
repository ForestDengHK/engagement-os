# Bid research discipline

How to fill the gaps a bid analysis surfaces with research that is comprehensive (depth AND
breadth), evidence-based, and zero-fabrication — so every claim that reaches the response can be
walked back to a real, verifiable source.

## Contents
- When to research
- Depth and breadth — both are required
- The two research streams
- Source discipline & tagging
- The zero-error / verification rule
- Output: the sourced research log
- Anti-patterns

## When to research

Research is driven by the **materials-needed list** from `rfp-analysis.md` Step 7 — specifically
the "we research" column and every matrix `gap`. Don't research at large; research to close named
gaps and to arm the high-weight win-themes with proof. Each research task names the Req ID(s) /
win-theme it serves.

## Depth and breadth — both are required

- **Breadth** = cover *every* topic the analysis flagged; no gap left dark. A bid loses on the
  requirement nobody researched.
- **Depth** = each topic grounded in a real source, not a generic assertion. One solid cited fact
  beats three hand-wavy ones.

Plan the research as a checklist of gaps, then work each to a cited answer or an explicit
`[⚠VERIFY] — could not source` (which must NOT then appear as a claim in the bid).

## The two research streams

- **External** (`[T3:OWN]` — our research of the outside world): market/sector context,
  competitor and incumbent intelligence, standards and regulations, comparable-outcome benchmarks,
  technology facts. Sourced from the web or authoritative documents; every item carries a URL /
  document locator.
- **Internal** (firm-held): our case studies, named-staff CVs, past-bid text, certifications,
  referees, pricing inputs. These come from the user's upload (the materials-needed "you upload"
  column), not the web. Cite the internal document and, if the win rests on it, ask the user to
  confirm the figure.

Keep the two visibly separate — an external market claim and an internal credential are different
kinds of evidence and are challenged differently.

## Source discipline & tagging

- **Primary over secondary.** A standard's own text beats a blog about it; a client's own
  published number beats an analyst's estimate.
- **Every claim carries a citation** — source name + locator (URL, page, clause) — using the same
  provenance tags as the rest of the pack (`references/provenance-and-precedence.md`): external
  research `[T3:OWN <source>]`, RFP facts `[RFP §x]`, unconfirmed `[⚠VERIFY vs <source>]`.
- **Recency + authority.** Prefer current, authoritative sources; note the date; flag anything
  that may have moved.

## The zero-error / verification rule

This is the hard gate the user set: **the bid cannot contain any error.**

- If a claim cannot be solidly sourced, it does **not** enter the response — it stays a
  `[⚠VERIFY]` in the research log with what would close it.
- No number, credential, or outcome is asserted without a citation a reviewer can open and check.
- When two sources disagree, keep both and apply precedence; never average or guess.
- Distinguish *fact* (cited) from *inference* (hedged, marked) — never let an inference read as a fact.

## Output: the sourced research log

Findings land in `bid_research_log.md` (one row per finding):

`# | Serves (Req/theme) | Claim | Stream (ext/int) | Source + locator | Tag | Confidence | Status`

The log is the bridge to `eng-bid-respond`: the response may only assert what the log has closed
with a citation. Open `[⚠VERIFY]` rows either get closed or are cut from the bid.

## Anti-patterns

- Fabricating or "rounding up" a credential, metric, or reference — an automatic disqualifier.
- A confident claim with no citation.
- Researching broadly but missing a flagged gap (breadth failure).
- Citing a secondary source when the primary was available.
- Letting an `[⚠VERIFY]` item quietly become a stated claim in the response.
