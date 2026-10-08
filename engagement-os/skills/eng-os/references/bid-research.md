# Bid research discipline

How to fill the gaps a bid analysis surfaces with research that is comprehensive (depth AND
breadth), evidence-based, and zero-fabrication — so every claim that reaches the response can be
walked back to a real, verifiable source.

## Contents
- When to research
- Depth and breadth — both are required
- The two research streams
- Required sweeps: network client stories and the buyer's agenda
- Source discipline & tagging
- The zero-error / verification rule
- Output: the sourced research log
- Anti-patterns

## When to research

Research is driven by the **materials-needed list** from `rfp-analysis.md` Step 7 — specifically
the "we research" column and every matrix `gap`. Don't research at large; research to close named
gaps and to arm the high-weight win-themes with proof. Each research task names the Req ID(s) /
win-theme it serves. Every `R` row in `3_drafting/commitments.md` is a research task too: the
row carries the question and the interim wording the response uses until the row closes.

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

## Required sweeps: network client stories and the buyer's agenda

Two sweeps run on every bid, whatever the gap list says.

**1. Firm network client stories in the buyer's sector.** Search the firm's public client-story
pages, its alliance pages (cloud and data vendors publish joint client stories) and the press.
Per story, capture:

| Field | Record |
|---|---|
| Client, as named publicly | the exact name the story uses |
| Member firm | which member firm delivered it |
| Year | publication or go-live year |
| Scope | what was delivered |
| Platform | the technology named |
| Measurable outcome | the figure the story states, or "none stated" |
| URL | the page, with access date |

Log each as a `[T3:OWN]` row with its source tier noted (firm page · alliance page · press). These
rows are reference candidates for `eng-bid-respond`'s rubric alongside the indexed firm assets.
On the worked example references were picked from what was on disk — a GenAI proof of concept,
an undated warehouse migration, a utility assessment — for an automotive buyer scoring
"automotive/manufacturing relevance"; an hour's public sweep then found network client stories
for three automotive and manufacturing clients.

**2. The buyer's next-12-months agenda.** Filings, separations and spin-offs, segment changes,
CEO letters, job ads. Each finding is a logged row; together they feed the response's "our
understanding" slide, so the response speaks to what the buyer is about to do, not only to the
RFP text.

## Source discipline & tagging

- **Primary before secondary.** A standard's own text beats a blog about it; a client's own
  published number beats an analyst's estimate. If only a secondary source exists, record the
  primary search and why it failed.
- **Atomic rows.** One independently checkable claim per row. Split compound claims.
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

Use the current `bid_research_log.md` template: atomic claim; fact/inference; stream; source type;
exact source+locator; publication/version; valid-as-of; recheck-by; tag; confidence; status.

The log is the bridge to `eng-bid-respond`: the response may only assert what the log has closed
with a citation. Open `[⚠VERIFY]` rows either get closed or are cut from the bid.

## Anti-patterns

- Fabricating or "rounding up" a credential, metric, or reference — an automatic disqualifier.
- A confident claim with no citation.
- Researching broadly but missing a flagged gap (breadth failure).
- Citing a secondary source when the primary was available.
- Letting an `[⚠VERIFY]` item quietly become a stated claim in the response.
