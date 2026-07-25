# Engagement OS — how to actually run it

Every scenario as: **what you type → what runs by itself → where it stops and needs you.**

There is no flag syntax. A command's arguments are plain text — write it however you'd say it,
and it asks for anything it still needs.

Legend: `[auto]` runs without you · `[drafts]` it writes a first version and shows you ·
`[decide]` a judgment call that's yours.

You are never sent to a text editor. Every artefact is drafted from what you already said and
presented inline; you correct it in the conversation and the agent writes the file.

---

## Scenario 1 — Research only

A client hands you material; you produce a report. No bid, no delivery.

```
▸ You type
    /eng-new   ACME, 27-010, "Market & Capability Study", research only

▸ What happens
    [asks]  where to put the repo (default ./acme-27-010)
    [auto]  scaffolds the research tree — 15 files
    [asks]  fills .claude/project-context.md from what you tell it
    [drafts] 5-8 questions for 00_research/README.md §1, derived from the goal
            you stated, shown inline
    [decide] ← you reshape them in chat ("drop 3, split 5"). It writes the file.
            This is the spine — every source and analysis file maps to one.

▸ You type   (once per batch of documents)
    /eng-source   ~/Downloads/acme-pack/

    [asks]  which bucket, if it can't tell how a doc was obtained
            (found in public → public/ · client gave it to you → engagement/)
    [auto]  converts each doc to markdown with §Page anchors, triages images,
            OCRs the unclear ones, writes the manifest row
    [auto]  folds facts into that bucket's 00_REFERENCE_SUMMARY.md,
            interpretation into 01_REFERENCE_INSIGHTS.md

▸ You type   (when the analysis is ready)
    /eng-sprint   the research report

    [auto]  validates the corpus — precedence conflicts, [⚠VERIFY] sweep
    [asks]  locks the report structure with you before writing content
    [auto]  builds into 00_research/2_output/, v0.1 → v1.0
    [asks]  review gate — every red-line resolved before it ships
    [auto]  records the live version in 00_research/README.md §4
```

**3 commands.** One decision that's genuinely yours: approving the question list.

<details><summary>What lands on disk</summary>

```
acme-27-010/
├── CLAUDE.md                      navigation index, built for this mode
├── .claude/project-context.md     the one place project facts live
├── 00_research/
│   ├── README.md                  ← YOUR questions + scope + live-output index
│   ├── 1_analysis/                one file per question
│   └── 2_output/                  the report, versioned
├── _sources/
│   ├── README.md                  which bucket, and the rules between them
│   ├── public/       SOURCES_GO_HERE.md + _md/{README,00_SUMMARY,01_INSIGHTS,images}
│   └── engagement/   SOURCES_GO_HERE.md + _md/{README,00_SUMMARY,01_INSIGHTS,images}
├── _pm/              engagement_log · raid_and_decisions · source_precedence_register
├── archived/  references/  panel/
```
</details>

---

## Scenario 2 — Pursuit only (bid a tender)

```
▸ You type
    /eng-new   ACME, tender 27-010, "DWH Strategic Assessment", bid only

    [auto]  scaffolds the bid tree — 16 files
    [asks]  fills project-context.md

▸ You type
    /eng-rfp   ~/Downloads/26-002-tender/

    [auto]  ingests the whole tender pack → 01_pursuit/27-010/1_received/_md/
            (anchored, so every requirement cites by clause/page)
    [auto]  fills compliance_matrix.md — one row per requirement, mandatory flagged
    [auto]  fills rfp_analysis.md — eval weights, multi-role read, win-themes, risks
    [asks]  ← STOP. GO / NO-GO. Yours to decide. On no-go it logs why and stops.
    [auto]  researches every open gap, cited; unsourceable → [⚠VERIFY] → cut
    [auto]  writes the response FROM the matrix, in the RFP's mandated format
    [asks]  red-team gate — mandatory requirements all met, format compliant
    [auto]  freezes to 4_final/
```

**2 commands.** One stop that's genuinely yours: go/no-go.

<details><summary>What lands on disk</summary>

```
acme-27-010/
├── 01_pursuit/
│   ├── 27-010/
│   │   ├── 1_received/_md/images/     the tender pack, converted
│   │   ├── 2_analysis/                ← compliance_matrix.md + rfp_analysis.md (planted)
│   │   ├── 3_drafting/                response working copies
│   │   ├── 4_final/                   what was submitted (frozen)
│   │   ├── 5_contracting/ 6_contract/ 7_briefing/
│   └── _shared/                       our reusable assets (CVs, case studies)
├── _sources/
│   ├── public/                        citable anywhere
│   └── pre_award/                     buyer-published + market research
├── _pm/  CLAUDE.md  .claude/  archived/  references/  panel/
```
Note there is **no `engagement/` bucket** — a bid has no post-award material yet.
</details>

---

## Scenario 3 — Delivery only

```
▸ You type
    /eng-new   ACME, 27-010, "DWH Strategic Assessment", delivery only

    [auto]  scaffolds the delivery tree — 19 files
    [asks]  fills project-context.md
    [drafts] the backbone for 3_findings/README.md, derived from the SOW / RFP
            requirements if either is ingested, else the sector-standard shape
    [decide] ← you add/cut/rename in chat. It writes the file.

▸ You type   (once per batch)
    /eng-source   ~/client-docs/
            same as scenario 1, but client material goes to engagement/

▸ You type   (once per session)
    /eng-workshop   week_1/session_2

    [drafts] the held-notes from whatever you supply — transcript, bullet dump,
            or a verbal recap: asked / answered / quotes / NOT covered
    [decide] ← it asks only about gaps ("nothing covers agenda item 4 — was it run?")
    [auto]  writes findings, one per topic, each tagged and mapped to the backbone
    [auto]  folds canonical deltas, updates the open-question backlog, logs it

▸ You type   (once per deliverable)
    /eng-sprint   D1

    [auto]  validates → [asks] locks structure → [auto] builds → [asks] review gate
    [auto]  updates DELIVERABLES.md to the new live version, archives the old
```

**4 commands**, the middle two on repeat. One decision that's genuinely yours: the backbone.

---

## Scenario 4 — Bid then deliver

```
▸ You type
    /eng-new   ACME, 27-010, "DWH Strategic Assessment", bid and delivery
    /eng-rfp   ~/Downloads/26-002-tender/
    ──────────── you win ────────────
    /eng-source     ~/client-docs/
    /eng-workshop   week_1/session_2
    /eng-sprint     D1
```

Scenario 2 then scenario 3. `bid and delivery` just builds both trees up front, so you don't
run `/eng-upgrade` later.

---

## Scenario 5 — Upgrading (you started with one lane, the scope grew)

```
▸ You type   (whichever applies)
    /eng-upgrade   we won the bid, add delivery
    /eng-upgrade   the study became the engagement, add delivery
    /eng-upgrade   the client is tendering, add pursuit

▸ What happens
    [auto]  re-scaffolds with old blocks + the new one. Everything existing
            prints `skip` — nothing is touched, nothing is overwritten.
    [auto]  updates CLAUDE.md itself — new pointer rows, skills line, phase.
            (The *script* won't clobber it, so the agent edits it and shows the diff.)
    [drafts] ← the handoff, from the compliance matrix + what was submitted in
            4_final/ + the RFP's dates. For a won bid that's
            01_pursuit/<id>/7_briefing/ — what we won, what we promised, scope,
            dates, the assumptions we priced. Delivery scope is read from HERE,
            not from anyone's memory of the bid.
    [asks]  ← re-baselines the sources (see below)

▸ Then
    carry on with the new lane's loop from scenario 1 / 2 / 3.
```

**1 command.** Then continue as normal.

### The two rules it will stop you on

**Winning verifies nothing.** A `pre_award/` fact stays `[T3]` after the win. The `engagement/`
bucket starts **empty** and fills only from what the client hands over post-award. Re-verify —
don't re-label.

**`engagement/` material can never enter a bid.** Not this bid, not a follow-on tender for the
same client. The material you know best is the material you may not use. Source it independently
or drop the claim.

---

## When you want one stage, not a whole chain

| | |
|---|---|
| `/eng-os` | the map — which stage owns what |
| `/eng-scaffold` | just create or extend the tree |
| `/eng-ingest-source` | convert exactly **one** document |
| `/eng-update-canonical` | fold an already-ingested batch into a bucket's summary |
| `/eng-write-findings` | evidence → findings |
| `/eng-validate-findings` | the precedence + `[⚠VERIFY]` sweep |
| `/eng-build-deliverable` | assemble from validated findings |
| `/eng-maintain-memory` | re-index CLAUDE.md / DELIVERABLES / project-context |
| `/eng-rfp-analyze` · `/eng-bid-research` · `/eng-bid-respond` | the three bid stages individually |

Default to the chain commands. A stage run in isolation skips the gates — that's how a
deliverable ends up built on unvalidated findings.

---

## The whole thing in one table

| Scenario | Commands | The one thing only you can do |
|---|---|---|
| Research | `/eng-new` → `/eng-source`* → `/eng-sprint` | approve the question list |
| Pursuit | `/eng-new` → `/eng-rfp` | the go/no-go call |
| Delivery | `/eng-new` → `/eng-source`* → `/eng-workshop`* → `/eng-sprint`* | approve the findings backbone |
| Bid then deliver | scenario 2, then scenario 3 | both of the above |
| Scope grew | `/eng-upgrade` → carry on | approve the handoff + re-baseline |
| Ship the file | `/eng-render <dir>` — standalone, any directory | decide document vs deck, and clear the gates |

`*` = repeat per batch / session / deliverable.

Self-test: `python3 skills/eng-os/scripts/verify_scenarios.py` scaffolds every scenario above and
checks each command resolves to a playbook whose skills and paths all exist.
