# The section-file contract

One section = one markdown file in `3_drafting/sections/` — or in a per-volume subdirectory
(`sections/v1/`, `v2/`, …) when the buyer mandates a volume split, in which case a figure is
referenced `../../figures/F-nn_x.png` and `figures/` stays shared at the `3_drafting/` level.
This document is the ONLY
definition of what that file carries and what the words in it mean. The template
(`templates/bid_section.md.tmpl`) plants it, `eng_lint.py` enforces it, and
`render_document.py` gates and strips by it — all three import the machine-readable
form (`scripts/section_contract.py`). If you change anything here, change the module
in the same commit; a contract defined in two places is already two contracts.

## Frontmatter fields

| Field | Meaning | Machine consumer |
|---|---|---|
| `section` | The buyer's own section number + title | render (used as the output title) |
| `rft_clause` | Where in the RFT this is demanded | none — documentation |
| `marks` | Points available | none — documentation |
| `pass_mark` | Minimum pass score, if any | none — documentation |
| `scoring` | HOW it is scored (per-item? as a whole?) | none — documentation, but it shapes the answer |
| `answers_reqs` | `[R-nnn, …]` compliance-matrix rows this section answers | lint — every id must exist in the matrix |
| `page_budget` | The limit AND its scope (see below) | lint — per-file and shared-pool checks |
| `figures` | `[F-nn, …]` this section uses | lint — every id must exist in `figures/` and be referenced in the body |
| `evidence` | `[A-nnn, …]` firm assets relied on | lint — every id must exist in `firm_assets.md` |
| `response_form` | `buyer-form: <their file>` · `buyer-structure` · `prose` — how the buyer expects THIS answer to arrive | lint — a clause with answer boxes may not be answered as free prose; a buyer-form must name its file |
| `depends_on` | Additional load-bearing inputs such as `commitments.md`, `estimation.xlsx`, `S-nn`, or a named analysis file. A section that cites any `[C-nn]` lists `commitments.md` | `eng-propagate-change` — a changed dependency invalidates this section's review |
| `status` | Lifecycle state (below) | lint + the render gate |
| `blocked_on` | Optional string: the external input that unblocks the section, and who owes it. Required when `status` is `blocked-rN` | lint — a `blocked-rN` section without it is an error |

A field with **no machine consumer is documentation**. Do not let it look enforced —
a field that appears checked but isn't is worse than no field (it reads as verified).
The documentation-only fields are still mandatory in the file: `marks`/`scoring` are
what a reviewer checks the answer's shape against.

Do not duplicate `answers_reqs`, `evidence`, or `figures` inside `depends_on`; those fields
already build their part of the graph. Use `depends_on` only where the dependency is otherwise
invisible — especially a pricing section that relies on `estimation.xlsx`.

## Status vocabulary (the only legal values)

Happy path: `draft → reviewed-r1 → reviewed-r2 → approved`

| Value | Means |
|---|---|
| `draft` | Being written; no review round has run |
| `reviewed-r1` / `reviewed-r2` | Round R1/R2 passed with no required changes |
| `revise-r1` / `revise-r2` | Round R1/R2 sent it back; changes owed |
| `blocked-r1` / `blocked-r2` | Round R1/R2 found something only an external input resolves (a date, a name, a fact); `blocked_on` names it |
| `approved` | R2 (experienced human) done; freezable |

Client-deliverable sections (delivery phase) use the plainer set:
`draft → reviewed → approved → issued`, with `revise` / `blocked` as the send-back states.

Anything else is invalid. `status` must agree with the **latest** verdict in the
review log: a `pass` verdict pairs with `reviewed-rN`/`approved`, `revise` with
`revise-rN`, `blocked` with `blocked-rN`. Lint checks the pairing, not just the two
extremes.

**Rounds iterate — append, never overwrite.** R1 sends a section back, the author fixes
it, R1 runs again. That is two rows: `R1` (verdict `revise`) then `R1 (2nd pass)`
(verdict `pass`), and the latest row is the one the status must agree with. Any label
beginning `R<digits>` is read as a round, so `R1b` and `R1 · re-check` work too. Never
edit the first row to make lint quiet: what R1 originally caught is the audit trail the
"one row per pass" rule exists to keep.

## `page_budget` format

`<N> A4[, shared across <which questions>][, <typography note>]`

- Per-file limit: `page_budget: "4 A4, Arial 10 (per section)"`
- Shared pool: every member of the pool carries the **same normalized string** —
  `page_budget: "5 A4 shared across 5.1.3 Q1-Q3, Arial 10"`. Lint normalizes dashes,
  case and whitespace before pooling, but keep the strings identical; the pool is
  checked once, as a total, because per-file checks on a shared budget always pass.

Estimate: ~525 words of Arial-10 prose per A4 side; a full-width figure costs ~half
a page. The estimate is a warning device; the build's printed PAGE COUNT is the truth.

## Scaffolding markers (stripped at render, under `bid`/`deliverable` only)

- `> **Internal note (stripped at render).** Sign-off: …` — one per section, REQUIRED, present
  even when empty (`Sign-off: none`). It lists what the section still owes as
  `[⚠VERIFY — owner: detail]` items, each matching a `commitments.md` row. It is the only place
  in a section file a `[⚠VERIFY]` may appear.

- `> **…**` blockquotes — scoring notes and reuse notes. Under the strict profiles a
  blockquote IS scaffolding by definition; never put real content (a quotation, a
  callout that must ship) in one. Every stripped run is reported on stderr.
- `**Traceability.** …` line — the claim-by-claim provenance.
- `**Figure source.** …` line — where a figure's editable master and PPTX live. It exists so a
  reviewer can correct the figure; an evaluator must never read our internal filenames, so the
  pointer goes on this line and NEVER in the figure caption. (Found for real: the template's own
  caption shipped `F-01_x.html` / `.pptx` straight into a rendered tender page.)
- `## Review log` section — one row per round: `| Round | Reviewer / lens | Date | Verdict | What changed |`.
  Verdicts: `pass` / `revise` / `blocked`. The verdict column is located by its
  header name, not by position.
- `[⚠VERIFY]` — an unresolved fact, inside the Internal note only. In body text the render gate
  blocks on it.

## Body text: values, no markers, no ids

Body text is everything outside the scaffolding above. It states each commitment's value in
words, copied verbatim from `commitments.md`, and carries no `[⚠VERIFY]` and no internal id
(`R-`, `A-`, `BR-`, `C-`). Ids go on the `**Traceability.**` line; open items go in the Internal
note.

## Figures: the editable-figure rule

Every figure lives in `3_drafting/figures/` as `F-nn_<name>.png` (goes in the document), and
it must be editable — a reviewer corrects the figure instead of describing the correction. A
figure is editable if it is drawn natively in the deck or has an editable companion (`.html`
master or `.pptx`). Sections reference the png: `![caption](../../figures/F-nn_<name>.png)` from
a volume directory (`sections/v1/`), `![caption](../figures/F-nn_<name>.png)` only from a flat
`sections/`. The caption itself is
client-facing text only — the editable-companion pointer belongs on the `**Figure source.**`
scaffolding line below it.
Design belongs to the `designing-figures` skill; the pipeline and export to its
render-pipeline reference. A missing companion is a lint warning; a missing png is
an error (pandoc degrades it to alt text — the document builds and the figure is gone).

## ID syntax

`R-nnn` requirement (compliance matrix) · `A-nnn` firm asset (`firm_assets.md`) ·
`F-nn` figure · `BR-nnn` research row (`bid_research_log.md`, cited in a body as `BR-003`
or `log #3`) · `C-nn` commitment (`3_drafting/commitments.md`, cited as `[C-nn]` on the
Traceability line only). Ids are allocated in their owning register and only there.

**Authored shorthand is not delivered shorthand.** Write `[RFP §3.3]`, `A-014`, `BR-005` and
`[C-07]` in the source, and `[⚠VERIFY — owner: detail]` in the Internal note: that is what makes
traceability checkable. The
render normalises them for the recipient — clause refs into the buyer's own vocabulary, unresolved
facts into a neutral `[TBD]`, internal ids **deleted**. Because deletion is the only possible
rendering of an id, a body sentence must not depend on one: put the id on the `**Traceability.**`
line and name the evidence in words. Lint warns (`internal-id-in-prose`) when it does not.

**A marker with an explanation is still the marker.** `[⚠VERIFY]` and
`[⚠VERIFY — what would close it]` are the same thing, and the explanatory form is the one
worth writing. Every matcher accepts both (`section_contract.VERIFY_RE`); a gate that
matched only the bare literal let eight markers reach a rendered tender page.
