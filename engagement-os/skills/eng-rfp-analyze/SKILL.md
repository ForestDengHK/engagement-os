---
name: eng-rfp-analyze
description: Use when an RFP / tender / ITT has arrived and needs decomposing before bidding, or the user says "analyse this RFP", "should we bid", "build the compliance matrix", "what does this tender need", or "break down the requirements". Produces a requirement/compliance matrix, an evaluation-weight score map, a multi-role analysis, evidence-backed win-themes, risk/deal-breaker flags, a materials-needed list (research vs upload), and a go/no-go — every claim cited to the RFP clause, nothing fabricated.
---

# Analysing an RFP

Decompose a tender into a scored, traceable analysis that drives a compliant, winning response.
Aligned twice — to the RFP text AND to our best practice — and read from every role's angle.
Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/rfp-analysis.md`.

## Prerequisite
The RFP pack is ingested to markdown first
(`Skill(engagement-os:eng-ingest-source)` → `01_pursuit/<ENG-ID>/1_received/_md/`)
so every requirement can be cited by clause/page.
**If missing:** no `_md/` pack → invoke `Skill(engagement-os:eng-ingest-source)` first
(no pursuit tree at all → `Skill(engagement-os:eng-scaffold)`, or just run `/eng-rfp`, which
chains both). Analysing from the raw PDF is how clause citations get invented.

Work in `01_pursuit/<ENG-ID>/2_analysis/`. **Three artefacts always, two on condition:**

| Artefact | When | What it carries |
|---|---|---|
| `rfp_analysis.md` | always | this skill's output |
| `compliance_matrix.md` | always | the completeness spine, one row per requirement |
| `clarification_log.md` | always | questions to the buyer + settled readings — the **query deadline lands before submission** |
| `bid_reuse_analysis.md` | **only if a prior bid exists** | section-by-section diff of what carries over |
| `estimation.xlsx` + generated `estimation.md` | **only if the tender is priced** | the maintained effort → cost model plus its diffable snapshot (`eng-estimate`) |

A conditional artefact exists **because the condition held, never because a list said so.** No
prior bid → don't create the file; record *"searched, none found"* in `rfp_analysis.md` §9. An
empty reuse analysis is worse than none — it reads as completed work.

One more lives a level up: `01_pursuit/_shared/firm_assets.md` — the index of what the firm
already holds, so the matrix's Evidence column names a file rather than a category, and an
expiring credential is visible before it fails a mandatory row.

## Workflow

```
RFP Analysis Progress:
- [ ] 1. Extract EVERY requirement → Req ID + clause cite + mandatory/desirable flag
- [ ] 2. Build compliance_matrix.md (one row per requirement)
- [ ] 2b. Decompose SCOPE → S-IDs + volumetric baseline + out-of-scope + unbounded language
- [ ] 2c. Our understanding & our solution — per challenge, incl. what we do NOT solve
- [ ] 3. Map evaluation criteria + weights → where we earn points
- [ ] 4. Multi-role analysis (panel lens) — record conflicts, don't smooth
- [ ] 5. Derive 3–5 evidence-backed win-themes (no proof → not a theme)
- [ ] 6. Flag risks / red-flags / deal-breakers (+ clarification questions)
- [ ] 7. Materials-needed list: WE research vs YOU upload (be specific)
- [ ] 7b. Prior-bid check — found one → bid_reuse_analysis.md; none → record the negative
- [ ] 8. Return the S-ID table to the RFP playbook for eng-estimate (priced tenders only)
- [ ] 9. When the estimate returns, finalise the go / no-go recommendation with conditions
```

Fill `rfp_analysis.md` (steps 2b–8) and `compliance_matrix.md` (step 2) from the templates in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

**Step 1 — completeness.** Read the whole RFP and every appendix/schedule. Extract *all*
obligations (scope, qualifications, submission mechanics, format rules, deadlines, weights,
contract terms), not just the obvious ones. Cite each: `[RFP §x]`.

**Step 2b — scope, or there is no estimate.** The matrix answers "did we address everything?",
not "how big is it": one row saying "conduct a comprehensive assessment of the Data Warehouse and
application landscape" is six weeks of work. Break the scope prose into numbered `S-01…` items,
each with the **effort driver** — the countable thing it scales on (source systems, interfaces,
reports, stakeholder groups, sites). Count them from the RFP and cite the count. Include the
scope items the RFP implies but never states — mobilisation, governance, QA, client review
cycles — or they come out of margin. An S-ID with no driver is not estimable; fix it here.
**Read the figures.** A tender's as-is architecture diagram is scope evidence, and it arrives as
an image — if `1_received/_md/` still shows `[caption-needed]` or `[uncertain]`, finish that
triage before decomposing, not after.

**Step 2c — understanding, then solution.** Per client challenge: their statement (cited) → what
we think is actually driving it → what we would do → **fully / partly / no** on whether that
resolves it → the *named* standard it conforms to ("industry best practice" is not one) → the
asset that proves we can do it. Then state plainly what our solution does **not** solve. This
section is the source text for the response's method and deliverables sections — usually where
the marks concentrate.

**Step 4 — multi-role.** Reuse the Panel Framework roles if installed (evaluator's-eye, solution
architect, engagement partner/commercial, legal, delivery lead, sector SME); else walk the lenses
manually. Each surfaces what a single reader misses.

**Step 7 — materials-needed.** Be specific ("the 2024 utility DWH case study with the €X saving",
not "a relevant case study"). This list is the input to `eng-bid-research` and the user's upload ask.

**Step 7b — prior bid: check, then record either way.** Search `01_pursuit/` and any `archive-*`
tree, and ask the user. Found → convert it and fill `bid_reuse_analysis.md` before drafting.
None → **create nothing** and write the negative into §9. A checked absence is a result; a
speculative file is a liability.

## Guardrails (the doctrine)
- **Nothing fabricated.** A capability/credential/metric we can't source becomes a materials-needed
  item or `[⚠VERIFY]` — never an asserted claim.
- **Dual alignment.** Every response approach maps to a requirement AND to our methodology.
- **Traceable both ways.** Requirement → our response; any claim → its requirement + evidence.

## Hand-off
Return the scope table (§3), gaps, materials-needed list, matrix, and win-themes to the
`rfp-arrived` playbook. It invokes `Skill(engagement-os:eng-estimate)` for priced tenders, then
returns here to finalise the clarification log and go/no-go recommendation. Do **not** invoke
research or drafting from this skill: only after the human GO gate does the playbook invoke
`Skill(engagement-os:eng-bid-research)` and `Skill(engagement-os:eng-bid-respond)`.
