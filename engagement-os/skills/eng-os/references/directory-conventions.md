# Directory, naming, and dual-index conventions

## Contents
- Placeholder legend
- The abstracted directory tree
- Structural rules worth preserving
- File-naming conventions
- The two "don't-grep-for-the-newest-file" indexes
- Template placeholders vs project-specific content

## Placeholder legend
`<CLIENT>` client short-code · `<ENG-ID>` engagement/tender id · `<Dn>` deliverable slot (D1…D6) · `<AREA>` discovery domain · `<TOPIC>` canonical reference topic · `<YYYY-MM-DD>` ISO date · `<vX.Y>` semantic deck/model version · `<Wn>` workshop/week number.

## The abstracted directory tree

```
<engagement-root>/
├── 01_pursuit/                         # BID / PURSUIT PHASE — frozen once won
│   ├── _shared/                        # cross-bid reusable assets (approaches, CVs, case studies, finance, diagrams)
│   ├── <ENG-ID>/                       # the live/won bid, one folder per tender id
│   │   ├── 1_received/                 # source RFP docs exactly as issued (never edited)
│   │   ├── 2_analysis/                 # our analysis: full-text md, Q&A, change-analysis vs prior issue
│   │   ├── 3_drafting/                 # response working copies + build scripts
│   │   ├── 4_final/                    # submitted response (Volume 1..n) — the frozen deliverable
│   │   ├── 5_contracting/              # SoW + contract review
│   │   ├── 6_contract/                 # signed contract + review trail
│   │   └── 7_briefing/                 # bid→delivery handoff briefing ("what we won / promised")
│   └── archive-<PRIOR-ID>/             # earlier/lost bids kept as reusable templates (audit trail)
│
├── 02_delivery/                        # DELIVERY PHASE — active
│   ├── _shared/
│   │   ├── compliance_research/        # standing regulatory/domain research, reused across findings
│   │   └── <client>_reference/         # RAW client-supplied source materials (native docx/pptx/pdf/xlsx)
│   │       └── _md/                    # CANONICAL markdown conversion of the raw pack (the SSOT knowledge base)
│   │           ├── 00_REFERENCE_SUMMARY.md   # roll-up of FACTS across all sources — "read first"
│   │           ├── 01_REFERENCE_INSIGHTS.md  # interpretive companion — deltas / risks / implications
│   │           ├── README.md                 # manifest: source→md map + conversion/OCR conventions
│   │           ├── NN_<TOPIC>/         # per-topic canonical folders (01_..., 02_..., NN_...)
│   │           └── images/<TOPIC>/     # extracted + OCR'd page/figure images, foldered by topic
│   ├── 0_mobilisation/                 # kickoff, onboarding, open-question backlog, handoff, decks/, meetings/
│   ├── 1_discovery/                    # current-state workshops + evidence gathering
│   │   ├── 1_inputs/                   # raw evidence: query packs + results, client docs, system-access, tool exports
│   │   ├── 2_workshops/                # 01_planned/ (per week) + 02_held/ (notes + transcripts, filled post-session)
│   │   ├── 3_findings/                 # per-area current-state findings, one file per topic
│   │   │   ├── README.md               # area list + the fixed "N-item backbone" every finding maps to
│   │   │   ├── _FINDING_STANDARD.md    # the single authority for finding-doc schema (planted from template)
│   │   │   └── <AREA>/                 # platform · data · reporting_bi · compliance · governance · operations · integration
│   │   └── 4_output/                   # consolidated discovery output artefacts (gate into D1)
│   ├── 2_assessment/                   # D1 — Current-State Assessment
│   ├── 3_target_architecture/          # D2 — Target / to-be architecture (options + recommendation)
│   ├── 4_roadmap/                      # D3 — Phased roadmap
│   ├── 5_cost_model/                   # D4 — Indicative cost model / TCO
│   ├── 6_executive_summary/            # D5 — Executive summary (+ D6 handover, bundled here)
│   ├── _pm/                            # RAID/status/governance, engagement_log.md, source-precedence register, forecast
│   └── DELIVERABLES.md                 # AUTHORITATIVE "which file is LIVE" index for D1..Dn
│
├── archived/                           # superseded artefacts, dated: superseded_decks_<DATE>/ (nothing deleted)
├── references/                         # Panel-Framework shared reference pack: compliance/ + delivery/ + index.md
├── panel/                              # Panel-Framework OUTPUTS ONLY: discussions/ drafts/ reviews/ debriefs/
├── .claude/                            # agent config: project-context.md, panel-config.yaml, agents/, templates/
└── CLAUDE.md                           # LEAN navigation index + SSOT pointer table; NOT a fact store
```

The deliverable folder names above (`2_assessment`…`6_executive_summary`) are the common data-strategy shape; rename them to the engagement's actual deliverable slots, but keep the **numeric-prefix + fixed D-number map** discipline.

## Structural rules worth preserving
- **Numeric phase prefixes** (`01_`, `02_`, then `0_mobilisation`…`6_executive_summary`) force chronological sort so the tree reads as the pipeline, top to bottom.
- **`_`-prefixed folders** (`_shared`, `_pm`, `_md`, `_deck_build`) sort to the top and signal "supporting, not a phase."
- **Deliverable folder ⇄ D-number is a fixed 1:1 map.** Findings' `Feeds:` lines depend on it, so it must be stable for the life of the engagement.
- **Raw vs canonical separation** under `_shared/<client>_reference/`: native files stay put; `_md/` is the derived, searched layer.
- **`01_planned/` vs `02_held/`** inside workshops — plan and actuals never overwrite each other.

## File-naming conventions

**Deliverables (client-facing decks/models):**
```
<CLIENT>_<ENG-ID>_D<n>_<Name>_v<X.Y>.pptx
<CLIENT>_<ENG-ID>_D<n>_<Name>_v<X.Y>.xlsx
```
- `v<X.Y>` semantic: `SKELETON` → `v0.1`…`v0.x` (drafts) → `v1.0` (client-issued) → `v2.x` (post-feedback).
- Every deck keeps a parallel `.pdf` render for review.
- `_SKELETON` = structure-only placeholder; archived once any `v0.1+` exists. A skeleton holds **no** real content (names/€/dates) — that is the content deck's job.
- `_INTERNAL` = never-shared working model; `_CLIENT` or unmarked = shareable. `_EDITABLE` marks the native-shapes source of a deck that also has a flattened/PDF twin.

**Working markdown inside a deliverable folder:**
```
00_D<n>_<name>_framework.md     # framework/skeleton seed — 00_ sorts it first
0N_<register_name>.md           # ordered registers: 01_..._synthesis, 02_..._register
<snake_case_topic>.md           # free working notes / synthesis (searchable, un-versioned)
```

**Findings:** `1_discovery/3_findings/<AREA>/<snake_case_topic>.md` — schema governed by `_FINDING_STANDARD.md`; the area folder IS the finding's `Area:`.

**Build/scratch (excluded from "deliverable" searches):** `_deck_build/`, `_model_build/`, `slide_redesign/`, `figures/`, `diagrams/`.

**Archival:** dated folders only — `archived/superseded_decks_<YYYY-MM-DD>/D<n>/…`. Nothing is deleted; things are moved with a date stamp.

**Panel outputs:** `panel/<kind>/<topic-slug>-<YYYY-MM-DD>.md` where `<kind>` ∈ `discussions|drafts|reviews|debriefs`.

## The two "don't-grep-for-the-newest-file" indexes

Decks rev fast and folders hold many versions + skeletons + build fragments. Two hand-maintained pointer files stop anyone from grabbing the wrong file.

**(a) `CLAUDE.md` → "Pointers to single-source-of-truth files" table.** CLAUDE.md is lean-by-design: a router, not a fact store. Columns: `Topic | Source-of-truth file | Use when`. Header rule: *only update CLAUDE.md when the navigation itself changes* — everything else updates the pointed-to file.

**(b) `02_delivery/DELIVERABLES.md` → the LIVE-file index.** The authoritative answer to "which `.pptx`/`.xlsx` is the current version of each `Dn`." Fixed sections:
1. Live deliverables table — `# | Deliverable | Current file (live path) | Format`.
2. Distinct annexes / historical decks kept in place (not the current answer).
3. "Where to search (and where NOT to)" — a table listing build-intermediate patterns (`_deck_build/`, `slide_redesign/`, `figures/`, `archived/`, `*_SKELETON.*`) as known sources of wrong hits.
4. Superseded (archived `<DATE>`) — what moved to `archived/` and when.

Together: **facts → project-context.md + `_md/` canon; live-file resolution → DELIVERABLES.md; navigation → CLAUDE.md.** No fact or pointer is duplicated across the three.

## Template placeholders vs project-specific content

**Ship as template (structure):** the whole folder skeleton; `_FINDING_STANDARD.md`; the findings `README.md` with a *parameterised* backbone; `DELIVERABLES.md` skeleton; the `CLAUDE.md` skeleton (empty pointer table + empty progress log); `.claude/project-context.md`; the `_md/` pack shape; naming *patterns* as format strings.

**Fill per engagement (content — never hardcode):** client identity & codes; stakeholder names/roles; the delivery-team roster; domain facts (products, tech stack, report counts, pillar names, vendor names); the *specific* backbone items; source-tier names; workshop numbering/dates; deliverable content and figures; reference-pack topics and compliance regimes.

**Rule of thumb:** if a string names *who the client is, what they run, who works on it, or a dated event* → content → placeholder. If it names *a phase, a folder role, a schema field, a naming pattern, or an index convention* → structure → ship it.
