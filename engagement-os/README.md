# Engagement OS — User Guide

**A delivery operating system for document-heavy consulting engagements.** Raw client
materials come in; defensible deliverables go out; every step in between is traceable.
The methodology is packaged as 8 skills + 4 composed workflows (playbooks) + 15
templates + 2 deterministic scripts, ready to land on day 1 of a new engagement.

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

After install the skills appear under the `engagement-os:eng-*` namespace. The Panel
Framework (`/panel-*`) is a companion review module, maintained separately.

## 2. What this is

One pipeline, one skill per stage, no overlapping authority:

```
scaffold ─► ingest ─► canonicalize ─► findings ─► validate ─► build deliverable
                                                          │            │
                                                  maintain memory   panel-review (hard ship gate)
                                                  (throughout)
```

| Skill | Job | Typical trigger |
|---|---|---|
| `eng-os` | Method map + shared assets (references / templates / scripts / playbooks) | Engagement start; finding a convention or workflow |
| `eng-scaffold` | Stand up the engagement repo (tree + CLAUDE.md + templates) → delegate to `/panel-init` | "set up a new engagement" |
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
that names the owning skill per step plus its stop gates. Four recurring situations:

| Situation | Playbook | Chain |
|---|---|---|
| **New source arrived** | `references/playbooks/new-source-arrived.md` | ingest (per doc) → canonicalize (per batch) → findings-impact check → log |
| **Post-workshop** | `references/playbooks/post-workshop.md` | held-notes → findings → canonical deltas → question backlog → log |
| **Deliverable sprint** | `references/playbooks/deliverable-sprint.md` | validate → panel-discuss (lock structure) → build → panel-review (red-line gate) → rev index |
| **New engagement, day 1** | `references/playbooks/new-engagement.md` | scaffold → fill context → panel-init → first ingest batch |

"Source arrives → OCR → canonical → finding" is exactly the first playbook. It is a
playbook rather than one fat skill because each stage also has its own standalone
trigger surface (findings also arise from workshops, bypassing ingest); duplicating
the stage content into a mega-skill would create a second truth that rots. Thin
orchestration gives the chained experience without duplication.

## 4. Day 1 of a new engagement

```bash
# 1. Scaffold (or say "set up a new engagement for <client> <id>" — eng-scaffold fires)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
  --root ./acme-27-010 --client ACME --eng-id 27-010 --name "Data Platform Strategic Assessment"

# 2. Fill what a machine can't know: project-context.md (stakeholders / pre-decisions /
#    constraints), the findings backbone, DELIVERABLES.md

# 3. /panel-init — builds roles from the same project-context.md

# 4. Drop client materials into the reference folder; ingest them one by one
#    (new-source-arrived playbook)
```

Adopting an existing repo with its own layout (adopt-in-place): don't rebuild the tree;
plant only the missing convention files (finding standard, reference-pack skeleton,
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

```
<engagement>/
├── CLAUDE.md                  ← navigation index, not a fact store
├── .claude/project-context.md ← the one source of project facts
├── DELIVERABLES.md            ← live-version index (check here first, never grep for the newest file)
├── 01_tender/                 ← bid phase (frozen)
├── 02_delivery/
│   ├── _shared/reference/     ← client originals + _md/ converted markdown
│   ├── 0_mobilisation/        ← discovery-question backlog
│   ├── 1_discovery/           ← workshops + 3_findings/ (findings by domain)
│   ├── 2_assessment/ … 6_executive_summary/
│   └── _pm/                   ← engagement log, source-precedence register, RAID
└── archived/                  ← superseded versions (audit trail, never deleted)
```

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
