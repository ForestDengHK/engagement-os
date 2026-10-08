# GREEN scenario — decide by default (eng-bid-respond, unknowns triage)

**Skill loaded:** `engagement-os:eng-bid-respond` (with `eng-os` references). **Fixture:** a scaffolded
pursuit repo with a settled `compliance_matrix.md`, `bid_research_log.md`, `firm_assets.md`, an
estimate, and a bid lead + delivery lead named in `.claude/project-context.md`.

## Task given to a fresh agent (verbatim)

```
Draft sections 3.1 (mobilisation & transition), 3.4 (service levels & hypercare) and 4.2
(commercial terms) of the response in 01_pursuit/<ENG-ID>/3_drafting/sections/v1/.
The RFP asks for: mobilisation period, hypercare length, P1/P2 response SLAs, rate hold period,
ISO 27001 certification, named service manager, delivery locations, and two client references.
Nothing in the repo states our mobilisation period, hypercare, SLAs or rate hold.
The ISO certificate and reference consent have not been confirmed by the firm.
Two writers will draft in parallel: you take 3.1 and 3.4, a second agent takes 4.2.
Use the plugin's templates. Do not ask me questions; I am unavailable until tomorrow.
When done, list every file you created or changed.
Deadline: submission is in two days.
```

## Pass criteria (all observable in the files)

1. `3_drafting/commitments.md` exists, from `commitments.md.tmpl`, with the eight columns
   `ID · Topic · Class (D/R/X) · Value as stated in the response · Basis / source · Approver · Status · Sections`.
2. ≥ 1 `D` row with a non-empty Basis (mobilisation, hypercare, SLAs and rate hold are all `D`, not `X`).
3. The ISO certificate and reference consent are `X` rows, each with fallback wording in the Value column.
4. Every section body (outside the Internal-note blockquote) contains **zero** `[⚠VERIFY`:
   `grep -c '\[⚠VERIFY' <body>` == 0 after removing lines starting `> **Internal note`.
5. Every section has exactly one `> **Internal note (stripped at render).** Sign-off:` line
   (`Sign-off: none` when nothing is owed).
6. Each section's Traceability line cites the `[C-nn]` rows its prose states; no `C-nn` appears in body prose.
7. Each `D`/`X` Value string appears verbatim in every section listed in its Sections column
   (consistency sweep: one hypercare value, one mobilisation value across all sections).
8. `3_drafting/signoff_sheet.md` exists with both tables ("Decisions to approve", "Firm inputs owed");
   the ISO and consent items are priority 1; the rate-hold decision is in "Decisions to approve".
9. Each section's `depends_on` lists `commitments.md`.

## Baseline failure (RED, observed 2026-10-07 under the previous skill)

- 160 `[⚠VERIFY — owner: …]` markers in section bodies across 21 sections. Bid lead: "too many
  TBD — if something we can decide, let's make the decision directly." Triage: 110 of 160 were
  bid-team decisions, 17 public facts, 33 firm-only.
- Parallel writers drifted: ISO wording three ways; hypercare "2 weeks" vs "4–8 weeks";
  mobilisation "10/30 working days" vs "10/20 business days"; rate hold "24 months" vs blank.
