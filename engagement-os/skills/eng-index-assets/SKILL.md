---
name: eng-index-assets
description: Use when our own reusable material must be turned into something a bid can cite — when case studies / CVs / credentials / methodology / rate cards are dropped into 01_pursuit/_shared/, when a colleague sends over "a case study we could use", or the user says "index what we have", "what can we evidence", "do we have anything for this requirement", "登记一下我们的资产". Also re-run whenever a new asset arrives mid-bid. Produces firm_assets.md — one row per asset stating what it PROVES, its date, whether it is in-window against this tender's recency rule, and its permission constraints — plus the gaps section that names what we cannot evidence.
---

# Indexing what the firm already holds

A folder answers *"what do we have"*. A bid needs *"what proves this requirement, and is it
still valid"* — and the second question is where bids are lost, because the answer is usually
found under deadline by someone who assumed it existed.

Output: `01_pursuit/_shared/firm_assets.md`. The material itself lives in
`01_pursuit/_shared/<kind>/` — what belongs there versus in `_sources/` is decided by where the
document came from; the folder's own `README.md` states the rule.

## If missing
No `_shared/` tree yet → run `eng-scaffold --mode pursuit` first. No assets yet → write the
**gaps** section anyway from the RFP's evidence requirements: knowing we can evidence nothing
for R-004 is the finding, and it is more useful early than complete-but-late.

## Workflow

```
- [ ] 1. Find this tender's RECENCY RULE first (e.g. "two projects within the last three
        years", "CVs no older than 12 months") — from compliance_matrix.md or the RFP. Without
        it there is no in-window verdict, and an undated asset cannot be triaged.
- [ ] 2. Read each asset. Not the filename — the document. Draft its row:
          What it PROVES = the claim an evaluator would score, in their language.
            ✗ "NorthGas data warehouse project"          (restates the title; unread)
            ✓ "end-to-end DWH assessment for a regulated utility, delivered in 12 weeks"
          Dated = the date the recency rule measures (usually completion, sometimes start —
            check which; if the RFP is ambiguous that is a clarification question, not a guess).
          In-window = yes / no / UNKNOWN against step 1's rule.
          Constraints = client permission? anonymisation needed? NDA? Unresolved permission
            is a blocker on the section that cites it, so it is recorded now, not at freeze.
- [ ] 3. Draft every row you can, THEN ask only the residual — with your best guess attached
        ("A-006 looks like 2023-11 from the report footer — confirm?"). Never hand back a
        blank table to fill in.
- [ ] 4. Map assets to requirements: which matrix row does each asset serve? An asset that
        serves none is not a gap in the bid — say so rather than padding the index.
- [ ] 5. Write the GAPS section: every evidence-bearing requirement with no in-window asset.
        Each gap gets a route: external research (→ eng-bid-research) or an upload request
        (→ a named human, with what exactly is needed).
- [ ] 6. Report back: how many requirements are now evidenced, which are UNKNOWN pending a
        date, which are genuine gaps and who owns each.
```

## The rules that decide the verdicts

- **Undated is unusable.** Recency rules are pass/fail; an asset whose date nobody can confirm
  cannot be cited no matter how good it is. `UNKNOWN` is a real state and must stay visible —
  it usually resolves into either a clarification question to the buyer or a five-minute check
  with the person who ran the project.
- **One asset can prove several things, and each is its own claim.** Split the row rather than
  writing a paragraph in the "proves" column; a section cites the claim, not the document.
- **Never invent an asset, a date, or a client name.** If we do not hold it, that is a gap with
  an owner — which is a usable answer. A fabricated credential is the one bid failure that
  survives the bid.
- **Anonymise by default when permission is unconfirmed**, and record that the anonymised
  version is what may be cited.

## Where it feeds

`eng-rfp-analyze` reads this index to decide which matrix rows are genuinely `gap`: a
requirement covered by an indexed, in-window asset is a **citation, not a gap**. Sections cite
assets by id in their `evidence:` frontmatter, and `eng_lint.py` checks every cited id exists
here — so an asset that never got a row silently fails a section that depends on it.
