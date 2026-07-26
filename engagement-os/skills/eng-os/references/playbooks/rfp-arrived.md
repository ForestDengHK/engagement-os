# Playbook: an RFP / tender arrives (the pursuit loop)

The bid lifecycle, from a tender landing to a submission-ready response. Each step names the
skill that owns it — follow that skill, don't reproduce it here. Runs in the `01_pursuit/<ENG-ID>/`
tree (`eng-scaffold --mode pursuit`; no delivery block is needed to bid).

## The shape

Six phases. The order matters more than the step count: **everything readable is in and citable
before anything is analysed**, and the analysis is closed before anything is written.

```
A. GATHER ──► B. ANALYSE ──► C. DECIDE 🛑 ──► D. CLOSE GAPS ──► E. WRITE ──► F. SHIP 🛑
  all material    the matrix     go/no-go        research          from the      red-team,
  in, converted,  + win-themes   (human)         what we           matrix,       lint, freeze,
  indexed                                        cannot yet        not free-     render
                                                 evidence          written
```

---

## Phase A — GATHER: everything in, converted, indexed

Three kinds of material arrive, with three different destinations. **Filing is decided by where
a document came from, never by what it is about** — a downloaded sector benchmark and a case
study we wrote are both "sector reference material", but only one can be freely quoted.

| What | Where it goes | Then |
|---|---|---|
| **the tender pack** — RFP, appendices, schedules, pricing workbook, draft contract | `01_pursuit/<ENG-ID>/1_received/` (never edited) | convert to anchored markdown in `1_received/_md/` |
| **reference material given to us or found by us** — buyer publications, sector/regulatory research, benchmarks, analyst material | `_sources/pre_award/` (buyer-specific) or `_sources/public/` (sector-wide) | convert + roll into that bucket's `00_REFERENCE_SUMMARY` / `01_REFERENCE_INSIGHTS` |
| **our own reusable assets** — methodology, case studies, CVs, credentials, diagrams, rate cards | `01_pursuit/_shared/<kind>/` (see its `README.md`) | index every one in `firm_assets.md`; convert to `01_pursuit/_shared/_md/` only if cited often |

**Nothing from `_sources/engagement/` may be cited in a bid** — not this engagement's, not
another client's. That bucket exists to make the boundary checkable, and `eng_lint.py` enforces it.

### A1. Run the source loop, once per batch → [new-source-arrived.md](new-source-arrived.md)
That playbook owns bucketing → `eng-ingest-source` → `eng-update-canonical`. It is the only
place the conversion mechanics live; this phase just says *what* to put through it. The lossless
image rule applies — a figure carrying a requirement is not allowed to be dropped silently.
**Verify:** every tender document is converted and citable by clause/page; every reference
document is in a bucket and summarised.

### A2. Check for a prior bid — BEFORE drafting anything
A re-issue, a follow-on, or the same buyer asking again means most of the answer already exists
*and already survived an evaluation*. Convert the prior response (`eng-ingest-source` →
`01_pursuit/archive-<PRIOR-ID>/`) and fill `bid_reuse_analysis.md`: section by section,
FULL REUSABLE / PARTIAL / REQUIRES UPDATE / NEW, with a field-level diff of the old clause
against the new one.
**Verify:** every section of the prior response has a verdict; every scope delta is named.
Skip only when there genuinely is no prior bid — say so rather than assuming.

### A3. Index what we already hold → `01_pursuit/_shared/firm_assets.md`
One row per asset: what it **proves** (the claim an evaluator would score, not the title), its
**date**, whether it is **in-window** against this tender's recency rule, and any
permission/confidentiality constraint.
A folder answers "what do we have"; a bid needs "what proves this requirement, and is it still
valid" — the second is where bids fail.
**Verify:** every asset has a date and an in-window verdict; the **gaps** section names what we
cannot evidence, so it becomes a research task or an upload request rather than a silent hole.

---

## Phase B — ANALYSE: decompose the tender against everything gathered

### B1. Check the procurement route
Planted in `rfp_analysis.md` by the scaffolder's `--variant`. The default is a full open RFP. A
**framework mini-competition** changes the loop: the buyer is pre-qualified, so the go/no-go
shrinks to capacity + conflict of interest; call-off terms are pre-agreed (commercial risk
review is narrower, not absent); and there may be **no clarification window** — check the
call-off before planning B3. The human stop at the go/no-go still applies either way.

### B2. Analyse the RFP → `eng-rfp-analyze`
Extract every requirement (ID + clause cite), build the `compliance_matrix.md`, map evaluation
weights, run the multi-role read, derive evidence-backed win-themes, flag risks/deal-breakers,
and produce the **materials-needed list** (research vs upload) and a go/no-go.
The firm-assets index from A3 is what makes a `gap` real: a requirement already covered by an
indexed, in-window asset is a citation, not a gap.
**Verify:** every requirement has a matrix row; every mandatory is flagged; go/no-go stated.

### B3. Raise clarifications before the query deadline → `clarification_log.md`
The query deadline is **earlier than the submission deadline** and it is hard: after it, an
ambiguity can only be handled by stating an assumption, which scores worse than an answer.
Sweep every `[⚠VERIFY]` and every matrix `gap` — anything the buyer could resolve becomes a
question. Log buyer-circulated answers as they arrive: they form part of the tender documents.
**Verify:** query deadline recorded; every load-bearing ambiguity either asked or given a
settled reading with a named consequence.

---

## Phase C — DECIDE 🛑 human

Go / no-go. If no-go, stop and log the rationale. If go-if, resolve the conditions first.
Only proceed on a go — this is the gate that stops research and writing effort being sunk into
a bid we won't win or can't deliver.

---

## Phase D — CLOSE GAPS → `eng-bid-research`

Close every matrix `gap` and arm the win-themes. A gap the index shows we cannot evidence needs
external research `[T3:OWN]` or an upload request. Every finding cited in `bid_research_log.md`;
zero fabrication. Sourced documents go back through Phase A's loop into `_sources/pre_award/`
or `_sources/public/` — never `_sources/engagement/`.
**Verify:** every gap is either closed with a citation or explicitly `[⚠VERIFY]` (and thus cut).

---

## Phase E — WRITE → `eng-bid-respond`

Build from the matrix (not free-written); match the RFP's mandated format exactly; compliance
first, then weave proof-backed win-themes; every claim traces to `[RFP §x]` or a closed research
log row. Draft in `3_drafting/`.

---

## Phase F — SHIP 🛑

1. **Red-team** → Panel Framework (`panel-review`) if installed, else a manual multi-lens pass
   (evaluator / legal / finance / architect). Clear the red-lines.
2. **Lint** — `python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/eng_lint.py <repo-root> --strict`.
3. **Freeze** to `4_final/`; record the submitted version + date.
4. **Render** the submission file → `eng-render --profile bid` (and `verify_deck.py` if a deck).

## Stop gates

- **STOP at Phase C** on a no-go — don't sink research/writing effort into a bid we won't win.
- **STOP and surface to the human** if research cannot source a claim a win-theme depends on
  (`[⚠VERIFY]` on a load-bearing claim) — that's a go/no-go re-check, not a wording fix.
- **STOP before submission** if any mandatory requirement is not `met` or any format rule is
  breached — format non-compliance is a common auto-reject. The lint in F2 decides the
  mandatory-row check, the `[⚠VERIFY]`-in-a-frozen-response check, and the bucket-leak check
  without a human re-reading the whole response.
