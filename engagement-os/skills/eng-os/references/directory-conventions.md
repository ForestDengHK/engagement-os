# Directory, naming, and dual-index conventions

## Contents
- Placeholder legend
- Composable blocks — pursuit / delivery / research
- The abstracted directory tree
- The `_sources/` boundary — why bid and delivery material stay apart
- Structural rules worth preserving
- File-naming conventions
- The two "don't-grep-for-the-newest-file" indexes
- Template placeholders vs project-specific content

## Placeholder legend
`<CLIENT>` client short-code · `<ENG-ID>` engagement/tender id · `<Dn>` deliverable slot (D1…D6) · `<AREA>` discovery domain · `<TOPIC>` canonical reference topic · `<YYYY-MM-DD>` ISO date · `<vX.Y>` semantic deck/model version · `<Wn>` workshop/week number.

## Composable blocks — pursuit / delivery / research

Not every engagement has both phases. A pursuit-only repo (we're just bidding), a delivery-only
repo (we were handed the work), and a standalone research assignment (client materials in, a
report out — no bid, no delivery) are all legitimate, and each should get **only** the tree it
needs — a half-empty delivery skeleton in a bid repo is noise that rots into wrong navigation.

The tree is therefore assembled from blocks. `eng-scaffold` builds the ones you name
(`--mode`, comma-separated to combine); **core is always built**.

| Block | Work tree it adds | Source bucket it needs | `--mode` |
|---|---|---|---|
| **core** (always) | `_pm/`, `.claude/project-context.md`, `CLAUDE.md`, `archived/`, `references/`, `panel/` | `public/` | — |
| **research** | `00_research/` (questions + `1_analysis/` + `2_output/`) | `engagement/` | `research` |
| **pursuit** | `01_pursuit/<ENG-ID>/…` + the `rfp_analysis` / `compliance_matrix` spine | `pre_award/` | `pursuit` |
| **delivery** | `02_delivery/…` + `DELIVERABLES.md` + the findings spine | `engagement/` | `delivery` |

`--mode full` (the default) = `pursuit,delivery` — the bid→delivery lifecycle. Research is a peer
block, not a lesser one: `--mode research,pursuit` is pre-bid intelligence feeding a tender.

**Research and delivery share the `engagement/` bucket** because they carry the same constraint —
in both, the client handed us material under an engagement's confidentiality terms. Buckets track
the constraint, not which work tree consumes them.

**Blocks are additive**: a research repo that later wins scope re-runs the scaffolder with a phase
block and nothing existing is touched. The one thing an additive run cannot do is extend an
already-written `CLAUDE.md` — its pointer table and skills list are mode-specific and must be
extended by hand (the scaffolder says so).

## The abstracted directory tree

Blocks are marked `[core]` / `[research]` / `[pursuit]` / `[delivery]`.

```
<engagement-root>/
├── _sources/                           # [core] ALL sourced material — bucketed by CONSTRAINT, never edited
│   ├── README.md                       # the bucket boundary + flow rules (read before filing anything)
│   ├── public/                         # [core]      unrestricted: public company info, sector/regulatory research, benchmarks
│   ├── pre_award/                      # [pursuit]   bid-scoped: what the buyer published + market research around the tender
│   └── engagement/                     # [research|delivery] restricted: client-internal, under this engagement's terms
│       ├── SOURCES_GO_HERE.md          # what belongs in THIS bucket
│       ├── <client's own taxonomy>/    # ORIGINALS (native docx/pptx/pdf/xlsx) — never renamed, never edited
│       └── _md/                        # CANONICAL markdown conversion — the searched layer, per bucket
│           ├── 00_REFERENCE_SUMMARY.md   # roll-up of FACTS in this bucket — "read first"
│           ├── 01_REFERENCE_INSIGHTS.md  # interpretive companion — deltas / risks / implications
│           ├── README.md                 # manifest: source→md map + conversion/OCR conventions
│           ├── NN_<TOPIC>/             # per-topic canonical folders (01_..., 02_..., NN_...)
│           └── images/<TOPIC>/         # extracted + OCR'd page/figure images, foldered by topic
│
├── _pm/                                # [core] engagement_log.md · raid_and_decisions.md · source-precedence register
│
├── 00_research/                        # [research] STANDALONE RESEARCH ASSIGNMENT — our own work, not sources
│   ├── README.md                       # the questions (the spine) · scope · the LIVE-output index
│   ├── 1_analysis/                     # working analysis, one file per question/theme, evidence cited inline
│   └── 2_output/                       # the report / brief / deck, versioned v0.x → v1.0
│
├── 01_pursuit/                         # [pursuit] BID PHASE — frozen once won
│   ├── _shared/                        # cross-bid reusable assets OF OURS — filed by KIND, not by topic
│   │   ├── README.md                   # what belongs here vs in _sources/ (decided by ORIGIN, not subject)
│   │   ├── firm_assets.md              # the index the bid consumes: what each asset PROVES + date + in-window
│   │   ├── approaches/ case_studies/ cvs/ credentials/ diagrams/ finance/
│   │   └── _md/                        # conversions of the above, when an asset is cited often enough to warrant one
│   ├── <ENG-ID>/                       # the live/won bid, one folder per tender id
│   │   ├── 1_received/                 # the tender pack exactly as issued (never edited) + _md/
│   │   ├── 2_analysis/                 # rfp_analysis.md · compliance_matrix.md · bid_research_log.md · Q&A
│   │   ├── 3_drafting/                 # response working copies + build scripts
│   │   ├── 4_final/                    # submitted response (Volume 1..n) — the frozen deliverable
│   │   ├── 5_contracting/              # SoW + contract review
│   │   ├── 6_contract/                 # signed contract + review trail
│   │   └── 7_briefing/                 # bid→delivery handoff briefing ("what we won / promised")
│   └── archive-<PRIOR-ID>/             # earlier/lost bids kept as reusable templates (audit trail)
│
├── 02_delivery/                        # [delivery] DELIVERY PHASE — active
│   ├── _shared/compliance_research/    # standing regulatory/domain research OF OURS, reused across findings
│   ├── 0_mobilisation/                 # kickoff, onboarding, discovery_questions.md, handoff, decks/, meetings/
│   ├── 1_discovery/                    # current-state workshops + evidence gathering
│   │   ├── 1_inputs/                   # raw evidence: query packs + results, system-access, tool exports
│   │   ├── 2_workshops/                # 01_planned/ (per week) + 02_held/ (notes + transcripts, filled post-session)
│   │   ├── 3_findings/                 # per-area current-state findings, one file per topic
│   │   │   ├── README.md               # area list + the fixed "N-item backbone" every finding maps to
│   │   │   ├── _FINDING_STANDARD.md    # the single authority for finding-doc schema (planted from template)
│   │   │   └── <AREA>/                 # platform · data · reporting_bi · compliance · governance · operations · integration · benchmark
│   │   └── 4_output/                   # consolidated discovery output artefacts (gate into D1)
│   ├── 2_assessment/                   # D1 — Current-State Assessment
│   ├── 3_target_architecture/          # D2 — Target / to-be architecture (options + recommendation)
│   ├── 4_roadmap/                      # D3 — Phased roadmap
│   ├── 5_cost_model/                   # D4 — Indicative cost model / TCO
│   ├── 6_executive_summary/            # D5 — Executive summary (+ D6 handover, bundled here)
│   └── DELIVERABLES.md                 # AUTHORITATIVE "which file is LIVE" index for D1..Dn
│
├── archived/                           # [core] superseded artefacts, dated: superseded_decks_<DATE>/ (nothing deleted)
├── references/                         # [core] Panel-Framework shared reference pack: compliance/ + delivery/ + index.md
├── panel/                              # [core] Panel-Framework OUTPUTS ONLY: discussions/ drafts/ reviews/ debriefs/
├── .claude/                            # [core] agent config: project-context.md, panel-config.yaml, agents/, templates/
└── CLAUDE.md                           # [core] LEAN navigation index + SSOT pointer table; NOT a fact store
```

The deliverable folder names above (`2_assessment`…`6_executive_summary`) are the common data-strategy shape; rename them to the engagement's actual deliverable slots, but keep the **numeric-prefix + fixed D-number map** discipline.

Don't confuse `_sources/` with the phase-level `_shared/` folders: `_sources/` holds material we
were **given or found**, bucketed by who may see it; `01_pursuit/_shared/` and
`02_delivery/_shared/` hold **our own** reusable assets and derived research.

## The `_sources/` boundary — why bid and delivery material stay apart

Material under different confidentiality constraints is not interchangeable and must never be pooled.
Pooling them breaks two things at once: the **evidence chain** (a pre-award assumption gets cited
downstream as a verified client fact) and **confidentiality** (post-award client-internal material
leaks into a later bid). Hence one bucket per provenance class, each with its **own**
summary/insights pair — a merged summary would destroy exactly the separation the buckets exist for.

**Flow rules:**
- `public/` → citable anywhere.
- `pre_award/` → `engagement/` **allowed on win**, but the fact does not upgrade with it: a pre-award
  claim stays `[T3]` until re-established from a delivery source or measured from the system.
- `engagement/` → `pre_award/` **forbidden**, in this bid or any later one. Source it independently.
- Promotion into `public/` requires the material to be genuinely public; when in doubt, it isn't.

**The tender pack is the one exception** — the RFP and appendices live in
`01_pursuit/<ENG-ID>/1_received/`, not `_sources/pre_award/`, because they are the contractual
artefact of *one* tender, frozen as issued and cited `[RFP §x]`. `_sources/pre_award/` holds the
pre-award material we *gathered around* it, which stays useful across tenders for the same buyer.

`_pm/source_precedence_and_conflict_register.md` is the **only** place allowed to reason across
buckets — that is what it is for.

## Structural rules worth preserving
- **Numeric phase prefixes** (`01_`, `02_`, then `0_mobilisation`…`6_executive_summary`) force chronological sort so the tree reads as the pipeline, top to bottom.
- **`_`-prefixed folders** (`_shared`, `_pm`, `_md`, `_deck_build`) sort to the top and signal "supporting, not a phase."
- **Deliverable folder ⇄ D-number is a fixed 1:1 map.** Findings' `Feeds:` lines depend on it, so it must be stable for the life of the engagement.
- **Raw vs canonical separation** inside every `_sources/<bucket>/`: native files stay put; `_md/` is the derived, searched layer.
- **`_`-prefixed roots are phase-independent.** `_sources/` and `_pm/` sit at the repo root, not inside a phase, precisely so a pursuit-only or research-only repo still has them. Anything scoped to one phase lives under that phase's numbered folder.
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

**(b) `02_delivery/DELIVERABLES.md` → the LIVE-file index** (delivery block). The authoritative answer to "which `.pptx`/`.xlsx` is the current version of each `Dn`." Fixed sections:
1. Live deliverables table — `# | Deliverable | Current file (live path) | Format`.
2. Distinct annexes / historical decks kept in place (not the current answer).
3. "Where to search (and where NOT to)" — a table listing build-intermediate patterns (`_deck_build/`, `slide_redesign/`, `figures/`, `archived/`, `*_SKELETON.*`) as known sources of wrong hits.
4. Superseded (archived `<DATE>`) — what moved to `archived/` and when.

Together: **facts → project-context.md + the per-bucket `_md/` canon; live-file resolution → DELIVERABLES.md; navigation → CLAUDE.md.** No fact or pointer is duplicated across the three.

In a **pursuit-only** repo the live-file question is "which response version is current" — the
equivalent index is the status column in `01_pursuit/<ENG-ID>/2_analysis/compliance_matrix.md`
plus the frozen `4_final/`. In a **research-only** repo there is no (b): the `_md/` manifest is
the whole index.

## Template placeholders vs project-specific content

**Ship as template (structure):** the whole folder skeleton; `_FINDING_STANDARD.md`; the findings `README.md` with a *parameterised* backbone; `DELIVERABLES.md` skeleton; the `CLAUDE.md` skeleton (empty pointer table + empty progress log); `.claude/project-context.md`; the `_md/` pack shape; naming *patterns* as format strings.

**Fill per engagement (content — never hardcode):** client identity & codes; stakeholder names/roles; the delivery-team roster; domain facts (products, tech stack, report counts, pillar names, vendor names); the *specific* backbone items; source-tier names; workshop numbering/dates; deliverable content and figures; reference-pack topics and compliance regimes.

**Rule of thumb:** if a string names *who the client is, what they run, who works on it, or a dated event* → content → placeholder. If it names *a phase, a folder role, a schema field, a naming pattern, or an index convention* → structure → ship it.
