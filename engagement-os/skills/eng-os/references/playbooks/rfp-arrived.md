# Playbook: an RFP / tender arrives (the pursuit loop)

The bid lifecycle, from a tender landing to a submission-ready response. Each step names the
skill that owns it — follow that skill, don't reproduce it here. Runs in the `01_pursuit/<ENG-ID>/`
tree (scaffolded by `eng-scaffold`).

## Chain

```
eng-ingest-source ─► eng-rfp-analyze ─► eng-bid-research ─► eng-bid-respond ─► panel red-team gate
   RFP → md            2_analysis          close the gaps      3_drafting → 4_final
```

1. **Ingest the RFP pack** → `eng-ingest-source`.
   Convert the RFP and every appendix/schedule to anchored markdown into
   `01_pursuit/<ENG-ID>/1_received/_md/` (pass the pursuit path to `--out`). Lossless image rule applies.
   Verify: every RFP document is converted and citable by clause/page.
2. **Analyse the RFP** → `eng-rfp-analyze`.
   Extract every requirement (ID + clause cite), build the `compliance_matrix.md`, map evaluation
   weights, run the multi-role read, derive evidence-backed win-themes, flag risks/deal-breakers,
   and produce the **materials-needed list** (research vs upload) and a go/no-go.
   Verify: every requirement has a matrix row; every mandatory is flagged; go/no-go stated.
3. **Go/No-Go gate — human decision.** If no-go, stop and log the rationale. If go-if, resolve the
   conditions first. Only proceed to research/response on a go.
4. **Research the gaps** → `eng-bid-research`.
   Close every matrix `gap` and arm the win-themes: external research `[T3:OWN]` + firm-held
   materials the user uploads. Every finding cited in `bid_research_log.md`; zero fabrication.
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
  format non-compliance is a common auto-reject.
