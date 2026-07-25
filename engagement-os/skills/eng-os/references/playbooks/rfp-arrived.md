# Playbook: an RFP / tender arrives (the pursuit loop)

The bid lifecycle, from a tender landing to a submission-ready response. Each step names the
skill that owns it — follow that skill, don't reproduce it here. Runs in the `01_pursuit/<ENG-ID>/`
tree (`eng-scaffold --mode pursuit`; no delivery block is needed to bid).

Sources: the tender pack lives in `1_received/`; pre-award background we gather goes to
`_sources/pre_award/`; public/sector research usable either side goes to `_sources/public/`.
**Nothing from `_sources/engagement/` may be cited in a bid** — not this engagement's, not another's.

## Chain

```
eng-ingest-source ─► reuse + assets ─► eng-rfp-analyze ─► clarify ─► eng-bid-research ─► eng-bid-respond ─► red-team
   RFP → md          prior bid? what     2_analysis        by the      close the gaps     3_drafting → 4_final
                     do we hold?                           deadline
```

1. **Ingest the RFP pack** → `eng-ingest-source`.
   Convert the RFP and every appendix/schedule to anchored markdown into
   `01_pursuit/<ENG-ID>/1_received/_md/` (pass the pursuit path to `--out`). Lossless image rule applies.
   Verify: every RFP document is converted and citable by clause/page.
1b. **Check for a prior bid FIRST — before drafting anything.** A re-issue, a follow-on, or the
   same buyer asking again means most of the answer already exists and already survived an
   evaluation. Convert the prior response (`eng-ingest-source` → `01_pursuit/archive-<PRIOR-ID>/`)
   and fill `bid_reuse_analysis.md`: section by section, FULL REUSABLE / PARTIAL / REQUIRES
   UPDATE / NEW, with a field-level diff of the old clause against the new one.
   Verify: every section of the prior response has a verdict; every scope delta is named.
   Skip only when there genuinely is no prior bid — say so rather than assuming.
1c. **Index what we already hold** → `01_pursuit/_shared/firm_assets.md`.
   Methodology, case studies, CVs, credentials, diagrams, financials. One row per asset: what it
   **proves** (the claim an evaluator would score, not the title), its **date**, whether it is
   **in-window** against this tender's recency rule, and any permission/confidentiality constraint.
   A folder answers "what do we have"; a bid needs "what proves this requirement, and is it still
   valid" — the second is where bids fail.
   Verify: every asset has a date and an in-window verdict; the **gaps** section names what we
   cannot evidence, so it becomes a research task or an upload request rather than a silent hole.
2. **Analyse the RFP** → `eng-rfp-analyze`.
   Extract every requirement (ID + clause cite), build the `compliance_matrix.md`, map evaluation
   weights, run the multi-role read, derive evidence-backed win-themes, flag risks/deal-breakers,
   and produce the **materials-needed list** (research vs upload) and a go/no-go.
   Verify: every requirement has a matrix row; every mandatory is flagged; go/no-go stated.
2b. **Raise clarifications before the query deadline** → `clarification_log.md`.
   The query deadline is **earlier than the submission deadline** and it is hard: after it, an
   ambiguity can only be handled by stating an assumption, which scores worse than an answer.
   Sweep every `[⚠VERIFY]` and every matrix `gap` — anything the buyer could resolve becomes a
   question. Log buyer-circulated answers as they arrive: they form part of the tender documents.
   Verify: query deadline recorded; every load-bearing ambiguity either asked or given a settled
   reading with a named consequence.
3. **Go/No-Go gate — human decision.** If no-go, stop and log the rationale. If go-if, resolve the
   conditions first. Only proceed to research/response on a go.
4. **Research the gaps** → `eng-bid-research`.
   Close every matrix `gap` and arm the win-themes. The **firm-assets index tells you which gaps
   are real** — a gap already covered by an indexed asset needs a citation, not research; a gap the
   index shows we cannot evidence needs external research `[T3:OWN]` or an upload request. Every finding cited in `bid_research_log.md`; zero fabrication.
   Sourced documents are ingested to `_sources/pre_award/` (buyer-specific) or `_sources/public/`
   (sector/regulatory/benchmark), never to `_sources/engagement/`.
   Verify: every gap is either closed with a citation or explicitly `[⚠VERIFY]` (and thus cut).
5. **Assemble the response** → `eng-bid-respond`.
   Build from the matrix (not free-written); match the RFP's mandated format exactly; compliance
   first, then weave proof-backed win-themes; every claim traces to `[RFP §x]` or a closed log row.
6. **Red-team gate** → Panel Framework (`panel-review`) if installed, else a manual multi-lens pass
   (evaluator / legal / finance / architect). Clear red-lines, then freeze to `4_final/` and record
   the submitted version + date.

## Stop gates

- **STOP at step 3** on a no-go — don't sink research/writing effort into a bid we won't win or can't deliver.
- **STOP and surface to the human** if research cannot source a claim a win-theme depends on
  (`[⚠VERIFY]` on a load-bearing claim) — that's a go/no-go re-check, not a wording fix.
- **STOP before submission** if any mandatory requirement is not `met` or any format rule is breached —
  format non-compliance is a common auto-reject. Run
  `python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/eng_lint.py <repo-root> --strict`: it
  decides the mandatory-row check, the `[⚠VERIFY]`-in-a-frozen-response check, and the
  bucket-leak check without a human re-reading the whole response.
