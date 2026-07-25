# Engagement OS — User Guide

**A composable operating system for document-heavy consulting engagements, bid to delivery.**
Raw client materials come in; defensible deliverables go out; every step in between is traceable.
Packaged as 11 skills + 6 playbook commands + 21 templates + 2 deterministic
scripts, ready to land on day 1 — and you scaffold only the part of the lifecycle you're
actually doing (bid only, delivery only, a standalone research assignment, or all of it).

> The agent-facing entry point is `skills/eng-os/SKILL.md` (auto-triggers). This file
> is the human-facing manual.

---

## 1. Install

Hosted in the `engagement-os` marketplace (this repo):

```
/plugin install engagement-os@engagement-os
```

Optional parser dependencies for `convert_source.py`:
`pip install pymupdf python-pptx python-docx openpyxl`
(Homebrew / PEP-668 Python: `pip install --user --break-system-packages pymupdf python-pptx python-docx openpyxl`, or use a venv.)

After install the skills appear under the `engagement-os:eng-*` namespace.

**Recommended companion:** the Panel Framework (red-line review gate, `/panel-*` skills):
```
/plugin marketplace add ForestDengHK/panel-framework
/plugin install panel-framework@panel-framework
```
engagement-os delegates to it when present and falls back to a documented manual
multi-lens review when it is not.

## 2. What this is

Two independent pipelines, one skill per stage, no overlapping authority:

```
PURSUIT   ingest RFP ─► analyse ─► research gaps ─► write response ─► red-team gate ─► submit

DELIVERY  scaffold ─► ingest ─► canonicalize ─► findings ─► validate ─► build deliverable
                                                        │            │
                                                maintain memory   panel-review (hard ship gate)
                                                (throughout)
```

Take either, both, or neither — see §4 for modes.

| Skill | Job | Typical trigger |
|---|---|---|
| `eng-os` | Method map + shared assets (references / templates / scripts / playbooks) | Engagement start; finding a convention or workflow |
| `eng-scaffold` | Stand up the repo for the blocks you need (`--mode`) → delegate to `/panel-init` | "set up a new engagement" |
| `eng-rfp-analyze` | Decompose an RFP: compliance matrix, eval-weight map, multi-role read, win-themes, go/no-go | A tender arrived |
| `eng-bid-research` | Close the analysis gaps with cited, zero-fabrication research | After RFP analysis, on a go |
| `eng-bid-respond` | Assemble the response from the matrix in the RFP's mandated format; red-team before submit | Writing the tender |
| `eng-ingest-source` | One document → anchored markdown; lossless image rule (decorative dropped / content kept / uncertain OCR'd) | A new source arrives |
| `eng-update-canonical` | Fold new facts into the canonical set: facts → SUMMARY, interpretation → INSIGHTS; conflicts superseded, never deleted | After ingest |
| `eng-write-findings` | Evidence → standards-conformant findings (severity/priority axes, evidence tags, backbone mapping) | After workshops; query results |
| `eng-validate-findings` | Corpus-wide provenance sweep: evidence-tag audit, precedence arbitration, `[⚠VERIFY]` register | Before deliverables; after an evidence wave |
| `eng-build-deliverable` | Validated findings → as-is / to-be deliverable (SKELETON → v0.x → v1.0) | "build D1/D2/…" |
| `eng-maintain-memory` | Keep CLAUDE.md / project-context / DELIVERABLES / cross-session memory lean (anti-rot) | Milestones; recurring corrections |

**Five load-bearing principles** (when a choice conflicts with one, the principle wins):
1. Source → derived separation — originals are never edited; every derivative traces back by path + page.
2. Single source of truth, referenced not copied — each fact lives in exactly one file.
3. A finding is a fact baseline, not a recommendation — observation and interpretation kept visibly separate.
4. Precedence resolves conflict; nothing is deleted — T1 system-measured > T2 workshop > T3 reference; the loser is stamped `⚠ superseded-by` and kept.
5. Lean by design — depth lives in dedicated files; indexes stay skimmable.

## 3. Composed workflows (Playbooks)

Skills compose **by orchestration, not duplication**: each playbook is a thin checklist
that names the owning skill per step plus its stop gates. Six recurring situations:

| Situation | Command | Chain |
|---|---|---|
| **New source arrived** | `/eng-source` | bucket it → ingest (per doc) → canonicalize (per bucket) → findings-impact check → log |
| **Post-workshop** | `/eng-workshop` | held-notes → findings → canonical deltas → question backlog → log |
| **Deliverable sprint** | `/eng-sprint` | validate → panel-discuss (lock structure) → build → panel-review (red-line gate) → rev index |
| **New engagement, day 1** | `/eng-new` | pick mode → scaffold → fill context → panel-init → first ingest batch |
| **An RFP arrived** | `/eng-rfp` | ingest RFP → analyse → go/no-go → research → respond → red-team |
| **The scope grew** (bid won, study became an engagement) | `/eng-upgrade` | re-scaffold with the added block → top up CLAUDE.md → write the handoff → re-baseline sources |

Each command is a thin router to `skills/eng-os/references/playbooks/<name>.md` — the playbook
holds the content, the command is just an explicit entry point. Saying the situation in words
works too; the commands exist for when you'd rather be deterministic than descriptive.

"Source arrives → OCR → canonical → finding" is exactly the first playbook. It is a
playbook rather than one fat skill because each stage also has its own standalone
trigger surface (findings also arise from workshops, bypassing ingest); duplicating
the stage content into a mega-skill would create a second truth that rots. Thin
orchestration gives the chained experience without duplication.

## 3b. Invoking things explicitly

Two surfaces, both typed with `/`. Skills auto-trigger from natural language; commands and skills
can also be called by name when you'd rather not rely on the trigger firing.

**Playbook commands** — a multi-step chain (one situation → several skills + stop gates):

```
/eng-new       /eng-rfp        /eng-source
/eng-upgrade   /eng-workshop   /eng-sprint
```

**Skills** — one stage, one job. Call directly when you know exactly which stage you want:

| Skill | Call it directly when |
|---|---|
| `/eng-os` | You want the map: which stage owns what, or a convention lookup |
| `/eng-scaffold` | Standing up a repo, or adding a block to one |
| `/eng-ingest-source` | Converting **one** document to citable markdown |
| `/eng-update-canonical` | Folding an ingested batch into a bucket's SUMMARY / INSIGHTS |
| `/eng-write-findings` | Turning evidence into findings |
| `/eng-validate-findings` | Running the corpus-wide precedence + `[⚠VERIFY]` sweep |
| `/eng-build-deliverable` | Assembling a deliverable from validated findings |
| `/eng-maintain-memory` | Re-indexing CLAUDE.md / DELIVERABLES / project-context |
| `/eng-rfp-analyze` | Decomposing an RFP into the compliance matrix |
| `/eng-bid-research` | Closing matrix gaps with cited research |
| `/eng-bid-respond` | Writing the tender response from the matrix |

Plugin skills are namespaced `engagement-os:eng-<name>`; the bare `/eng-<name>` form works when
it's unambiguous. Arguments are free text and get passed through — `/eng-new ACME 27-010 mode=pursuit`.

**Which surface to use.** Reach for the **command** when the situation is the unit of work ("a
doc arrived", "we won") — it carries the ordering and the stop gates, which are the part that's
easy to skip. Reach for the **skill** when you want exactly one stage and nothing else. When in
doubt use the command: running one stage of a chain in isolation is how a deliverable ends up
built on unvalidated findings.

## 4. Pick your lane

Three lanes, independent. Build only what the work actually is — an empty `02_delivery/` in a bid
repo sends every later skill hunting through folders that will never hold anything.

| The work is… | `--mode` | You get |
|---|---|---|
| A standalone research assignment — materials in, a report out | `research` | `00_research/` + `public` `engagement` buckets |
| Bid only — respond to an RFP | `pursuit` | `01_pursuit/<ENG-ID>/` + `public` `pre_award` buckets |
| Delivery only — we already have the work | `delivery` | `02_delivery/` + `public` `engagement` buckets |
| Bid then deliver | `full` *(default)* | both phase trees + all three buckets |

Comma-combine to mix (`pursuit,delivery` ≡ `full`; `research,pursuit` = pre-bid intelligence
feeding a tender). Every lane also gets core: `CLAUDE.md`, `project-context.md`, `_pm/`,
`_sources/README.md`, `archived/`, `references/`, `panel/`.

Everything below starts the same way — **say it in words and `eng-scaffold` fires** ("set up a
research repo for ACME", "we're bidding ACME 27-010"), or run the script directly:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
  --root ./acme-27-010 --client ACME --eng-id 27-010 --name "<engagement name>" --mode <lane>
```

Then, in every lane: fill `.claude/project-context.md` (the facts a machine can't know), and run
`/panel-init` if you have the Panel Framework.

### Lane A — research (`--mode research`)

```
1. Write the questions       00_research/README.md — bounded, answerable; this is the spine.
                             Do this BEFORE ingesting, or sourced facts land nowhere.
2. Ingest sources            "ingest this doc" → eng-ingest-source, one doc at a time.
                             Bucket by how you got it: found in public → public/;
                             client gave it to you → engagement/.
3. Canonicalize              eng-update-canonical → facts to 00_REFERENCE_SUMMARY,
                             interpretation to 01_REFERENCE_INSIGHTS, per bucket.
4. Analyse                   00_research/1_analysis/, one file per question, evidence cited
                             inline back to <bucket>/_md/<file>.md §Page N.
5. Write the output          00_research/2_output/, v0.1 → v1.0. Close or cut every
                             [⚠VERIFY] first — an unsourceable claim never ships.
6. Review, then issue        panel-review (or a manual multi-lens pass). Record the live
                             version in 00_research/README.md §4.
```

### Lane B — pursuit (`--mode pursuit`)

```
1. Ingest the tender         → 01_pursuit/<ENG-ID>/1_received/_md/ (the RFP is the contractual
                             artefact, cited [RFP §x]). Background research → pre_award/.
2. Analyse the RFP           eng-rfp-analyze → fills the planted rfp_analysis.md +
                             compliance_matrix.md: every requirement gets a row, eval weights
                             mapped, win-themes, risks, materials-needed, go/no-go.
3. GO / NO-GO — human        Stop here on a no-go and log why. Don't sink writing effort
                             into a bid you won't win or can't deliver.
4. Research the gaps         eng-bid-research → close every matrix `gap` with a citation.
                             Zero fabrication; unsourceable → [⚠VERIFY] → cut.
5. Write the response        eng-bid-respond → built FROM the matrix, in the RFP's mandated
                             format. Every claim traces to [RFP §x] or a closed log row.
6. Red-team, then submit     panel-review. Freeze to 4_final/ and record what was submitted.
```

### Lane C — delivery (`--mode delivery`)

```
1. Set the backbone          02_delivery/1_discovery/3_findings/README.md — the fixed problem
                             list every finding maps to. The one structural choice to make
                             deliberately up front.
2. Ingest + canonicalize     Client materials → engagement/ bucket → eng-ingest-source →
                             eng-update-canonical. (new-source-arrived playbook)
3. Workshops → findings      eng-write-findings — a finding is a FACT BASELINE, not a
                             recommendation. (post-workshop playbook)
4. Validate                  eng-validate-findings — corpus-wide precedence sweep, evidence-tag
                             audit, [⚠VERIFY] register. Run before any deliverable.
5. Build deliverables        panel-discuss locks the structure → eng-build-deliverable →
                             panel-review is the hard ship gate. (deliverable-sprint playbook)
6. Keep the index honest     Update DELIVERABLES.md to the new version; archive the old one.
```

## 4b. Upgrading — the scope grew

You bid, you won. Or the study became the engagement. **Don't rebuild and don't fork a second
repo** — add the block and keep one audit trail. Full chain + gates:
`references/playbooks/adding-a-block.md`.

```bash
# Name the OLD blocks AND the new one — --mode is the repo's full block list, not a delta.
python3 .../scaffold_engagement.py --root <same root> ... --mode pursuit,delivery
```

Everything that exists prints `skip`; only the new block's tree, bucket, and templates appear.
Then three things the script can't do for you:

| # | Do this | Why |
|---|---|---|
| 1 | **Top up `CLAUDE.md` by hand** — new pointer rows, skills line, `**Phase:**` | The scaffolder never rewrites an existing `CLAUDE.md`; it warns when a block was added |
| 2 | **Write the handoff** — for a won bid, `01_pursuit/<ENG-ID>/7_briefing/`: what we won, what we promised, scope, dates, priced assumptions | Delivery scope gets read from here, not from memory of the bid. Skipping it is the most expensive failure mode of a won bid |
| 3 | **Re-baseline the sources** | See below — this is the one that bites |

**The gate that matters: winning verifies nothing.** A `pre_award/` fact stays `[T3]` after the
win; the `engagement/` bucket starts **empty** and fills from what the client hands over
post-award. Re-verify, don't re-label — and log the re-baseline in the precedence register.

**And the sharp edge in the other direction:** when a delivery client tenders again, *everything*
in `engagement/` is off-limits to that bid. The material you know best is the material you may not
use. There is no "we already know it" exception — source it independently or drop the claim.

Adopting an existing repo with its own layout (adopt-in-place): don't rebuild the tree;
plant only the missing convention files (finding standard, source-bucket skeleton,
DELIVERABLES index) and record the mapping in CLAUDE.md.

## 5. Everyday cheat sheet

| I want to… | Do this |
|---|---|
| A new PDF/deck arrived from the client | "ingest this doc" → the new-source-arrived chain fires |
| A workshop just ended | Fill held-notes, then "write this up as findings" → post-workshop chain |
| Two sources disagree | Nothing manual — canonicalization arbitrates T1>T2>T3; loser stamped superseded, kept |
| A fact isn't verifiable yet | Tag `[⚠VERIFY]` + V-n register row; validate tracks its lifecycle |
| Ship a deliverable | "validate the findings" → panel-discuss locks structure → build → panel-review is the hard gate |
| A deliverable rev'd again | Update only `DELIVERABLES.md` to point at the new version; archive the old one, never delete |
| Same correction happened twice | "record this as a memory" → bake it into the convention file, not conversation memory |

## 6. What a scaffolded repo looks like

Blocks marked `[core]` / `[research]` / `[pursuit]` / `[delivery]` — you get core plus whichever
you selected. Source buckets follow the blocks: core always gets `public/`; `pursuit` adds
`pre_award/`; `research` and `delivery` add `engagement/`.

```
<engagement>/
├── CLAUDE.md                  ← [core] navigation index, not a fact store (built for your mode)
├── .claude/project-context.md ← [core] the one source of project facts
├── _sources/                  ← [core] ALL sourced material, BUCKETED BY CONSTRAINT
│   ├── README.md              ←   the bucket boundary + flow rules
│   ├── public/                ←   [core]      unrestricted — citable anywhere
│   ├── pre_award/             ←   [pursuit]   bid-scoped — must stay usable if we lose
│   └── engagement/            ←   [research|delivery] restricted — never travels into a bid
│       └── _md/               ←   each bucket: originals + its OWN converted markdown + summary/insights
├── _pm/                       ← [core] engagement log, source-precedence register, RAID + decisions
├── 00_research/               ← [research] questions + scope, 1_analysis/, 2_output/ (+ live-output index)
├── 01_pursuit/<ENG-ID>/       ← [pursuit] tender pack, RFP analysis + compliance matrix, drafting, final
├── 02_delivery/               ← [delivery]
│   ├── 0_mobilisation/        ←   discovery-question backlog
│   ├── 1_discovery/           ←   workshops + 3_findings/ (findings by domain)
│   ├── 2_assessment/ … 6_executive_summary/
│   └── DELIVERABLES.md        ←   live-version index (check here, never grep for the newest file)
└── archived/                  ← [core] superseded versions (audit trail, never deleted)
```

**Why `_sources/` is split three ways — and why by constraint, not by phase.** A bucket answers
one question: *who may see this, and where may we use it.* That answer is the same whether you're
bidding, delivering, or running a standalone research assignment — so the same filing rule works
in every mode, and a research assignment's client material lands in `engagement/` where it
belongs instead of being mislabelled as public.

Pooling classes would break two things at once: the **evidence chain** (a pre-award assumption
resurfaces downstream as a verified client fact) and **confidentiality** (restricted material
leaks into a later bid). So each bucket keeps its own summary/insights pair;
`engagement/ → pre_award/` is forbidden; `pre_award/ → engagement/` is allowed on win but the
fact stays `[T3]` until re-established. The source-precedence register is the only place allowed
to reason across buckets.

**Sources vs work.** `_sources/` is only what we were *given or found*. What we *write* goes in a
work tree — `00_research/1_analysis/`, `01_pursuit/<ENG-ID>/2_analysis/`, or `02_delivery/`.

## 7. FAQ

- **Do the skills step on each other?** No — seam contract: only `eng-update-canonical`
  edits the canonical set; only `eng-validate-findings` runs the corpus-wide sweep;
  `eng-build-deliverable` consumes only validated findings.
- **Does it work without the Panel Framework?** Yes. Panel is a companion; scaffold
  delegates to `/panel-init` when present and skips it otherwise. Any equivalent
  review mechanism can stand in for the ship gate.
- **Any client content baked into the templates?** None. The pack ships structure and
  discipline only — identity, domain facts, and backbone items are filled per engagement.
- **Hardcoded paths?** None. Skills reference shared assets via `${CLAUDE_PLUGIN_ROOT}`.

---

*Distilled from a live data-strategy delivery engagement (2026). Ships structure + discipline, never client content.*
