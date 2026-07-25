---
name: eng-os
description: Use when starting or running a document-heavy consulting / advisory engagement across both the pursuit/bid side (analyse an RFP, research, write a tender response) and the delivery side (assessment, target architecture, roadmap, cost model, exec summary); when you need the pipeline map, the shared conventions (finding schema, source-precedence, directory rules, memory discipline), or a composed multi-stage playbook (new source, post-workshop, deliverable sprint, new engagement, RFP-arrived); or when deciding which eng-* stage skill applies (pursuit: rfp-analyze / bid-research / bid-respond; delivery: scaffold / ingest / canonicalize / findings / validate / build).
---

# Engagement OS

A repeatable operating model for consulting engagements that run on documents:
raw client materials come in, and defensible client deliverables go out — with a
traceable chain between them so every claim in a deck can be walked back to its source.

This skill is the **map**. It explains the pipeline and points to the one skill that
owns each stage. The deep conventions live in `references/`; the fill-in artefacts
live in `templates/`; deterministic helpers live in `scripts/`.

## Two pipelines, composable — take only what the work needs

The pursuit side and the delivery side are **independent**, and a standalone research assignment
is a third peer. `eng-scaffold --mode` builds only the blocks you name — `research` · `pursuit` ·
`delivery` · `full` (default, = pursuit + delivery); comma-combine to mix, and re-run later to add
a block without touching what exists.

| Block | Work tree | Source bucket it needs |
|---|---|---|
| core (always) | `_pm/` · `CLAUDE.md` · `project-context.md` | `public/` |
| `research` | `00_research/` — questions · `1_analysis/` · `2_output/` | `engagement/` |
| `pursuit` | `01_pursuit/<ENG-ID>/` | `pre_award/` |
| `delivery` | `02_delivery/` | `engagement/` |

Source material is bucketed by **confidentiality constraint**, not by phase — a bucket answers
"who may see this, and where may we use it", and that answer is the same in every mode. Each
bucket keeps its own summary/insights pair; pooling them would both corrupt the evidence chain
and leak restricted material into later bids. Research and delivery share `engagement/` because
they carry the same constraint. Boundary + flow rules:
[references/directory-conventions.md](references/directory-conventions.md).

**`_sources/` is what we were given or found; work trees are what we write.** Never put our own
analysis in `_sources/`.

## The delivery pipeline (one job per stage)

```
                                              ┌─ panel-discuss (lock structure)
                                              │
scaffold ─► ingest ─► canonicalize ─► findings ─► validate ─► build deliverable
   │           │           │             │           │              │
   │           │           │             │           │              └─ panel-review (gate)
   │           │           │             │           └─ maintain memory (throughout)
```

| Stage | Skill | What it does |
|---|---|---|
| **Scaffold** | `eng-scaffold` | Stand up the repo for the selected blocks (`--mode`), then delegate to `/panel-init`. Serves both pipelines. |
| **Ingest** | `eng-ingest-source` | Convert ONE client/reference document to faithful, citable markdown with lossless image/OCR handling + a manifest row. |
| **Canonicalize** | `eng-update-canonical` | Fold new facts into the canonical `00_REFERENCE_SUMMARY` (facts) and `01_REFERENCE_INSIGHTS` (interpretation), keeping provenance. |
| **Findings** | `eng-write-findings` | Turn evidence into standards-conformant current-state findings (severity/priority, evidence tags, precedence tags, backbone mapping). |
| **Validate** | `eng-validate-findings` | Provenance/validation sweep: evidence-tag audit, precedence arbitration, `[⚠VERIFY]` register, backbone + canonical alignment. |
| **Build** | `eng-build-deliverable` | Assemble an as-is / to-be deliverable from *validated* findings, provenance intact; add each deliverable's own so-what. |
| **Memory** | `eng-maintain-memory` | Keep CLAUDE.md / project-context / DELIVERABLES / cross-session memory canonical and lean (anti-rot). Runs throughout. |
| **Review** | Panel Framework (companion) | `panel-discuss` locks a deliverable's structure; `panel-review` is the hard red-line gate before anything ships; `panel-debrief` after workshops. |

## The pursuit pipeline (bid side — win the work first)

Before delivery there's the bid. Same document-and-provenance discipline, aimed at a compliant,
winning tender. Runs in `01_pursuit/<ENG-ID>/`, sourced from `_sources/pre_award/` + `_sources/public/`.

```
ingest RFP ─► analyse ─► research gaps ─► write response ─► panel red-team gate ─► submit
```

| Stage | Skill | What it does |
|---|---|---|
| **Analyse** | `eng-rfp-analyze` | Decompose the RFP: requirement/compliance matrix, evaluation-weight map, multi-role read, evidence-backed win-themes, risks/deal-breakers, materials-needed list, go/no-go. |
| **Research** | `eng-bid-research` | Close the analysis gaps with comprehensive, cited, zero-fabrication research (external `[T3:OWN]` + firm-held uploads). |
| **Respond** | `eng-bid-respond` | Assemble the response from the matrix, matching the RFP's mandated format; compliance-first, proof-backed win-themes, every claim traceable; red-team before submit. |

(RFP intake reuses `eng-ingest-source`; the RFP is the pursuit-side source of record — tag facts `[RFP §x]`.)

## The six load-bearing principles

Everything in this pack exists to protect these. If a choice conflicts with one, the principle wins.

1. **Source → derived separation.** Originals are never edited. Every derived markdown, finding, and slide traces back to an original by path + page/slide. Provenance is a first-class citizen, not an afterthought.
2. **Single source of truth, referenced not copied.** Each fact lives in exactly one file; everything else *links* to it. Deliverable versions live only in `DELIVERABLES.md`; project facts only in `.claude/project-context.md`; CLAUDE.md is a router, never a fact store. The one deliberate *non*-merge: each `_sources/` bucket keeps its own summary, because bid and delivery corpora must not pool.
3. **A finding is a fact baseline, not a recommendation.** Findings record what *is* (observation and interpretation kept visibly separate) so every downstream deliverable can cite the same fact with its own so-what, without re-pasting evidence.
4. **Precedence resolves conflict; nothing is deleted.** Measured-from-the-system beats the workshop room beats the vendor deck (T1 > T2 > T3). On conflict, keep both and stamp the loser `⚠ superseded-by`. Unverifiable claims are gated with `[⚠VERIFY]`.
5. **Lean by design.** Depth lives in dedicated files; the index stays skimmable. CLAUDE.md and canonical summaries are updated on *milestones and material change*, not every edit.
6. **Draft first, ask second — never send the user to an editor.** Templates exist so the *agent* fills them, not so a human is handed a blank form. Draft from what's already available (invocation text, project-context, ingested RFP/SOW, manifests), show it inline, ask only the residual with your recommendation stated, then write the file. A workflow step whose instruction is "now go write X.md" is mis-designed. → [references/guided-elicitation.md](references/guided-elicitation.md)

## Conventions — read the reference file that matches your task

Keep these one level away; read the specific file when the stage needs it.

- **Directory + composable blocks + the `_sources/` bucket boundary + dual-index discipline** → [references/directory-conventions.md](references/directory-conventions.md)
- **Ingestion, lossless image/OCR rule, facts-vs-insights canonical split** → [references/canonical-reference.md](references/canonical-reference.md)
- **Finding schema — severity vs priority, evidence tags, body shapes** → [references/finding-standard.md](references/finding-standard.md)
- **Source precedence (T1/T2/T3), `[⚠VERIFY]`/V-n register, conflict clusters** → [references/provenance-and-precedence.md](references/provenance-and-precedence.md)
- **As-is / to-be assembly, versioning, the panel gate** → [references/deliverable-build.md](references/deliverable-build.md)
- **CLAUDE.md / project-context / DELIVERABLES / memory discipline (incl. AGENTS.md)** → [references/memory-discipline.md](references/memory-discipline.md)
- **Guided elicitation — how to fill an artefact WITH the user instead of handing them a blank** → [references/guided-elicitation.md](references/guided-elicitation.md)
- **RFP decomposition — compliance matrix, eval-weight map, multi-role read, win-themes, go/no-go** → [references/rfp-analysis.md](references/rfp-analysis.md)
- **Bid research — depth+breadth, source discipline, zero-fabrication, the [⚠VERIFY] gate** → [references/bid-research.md](references/bid-research.md)
- **Bid response — requirement-driven assembly, format-match, traceability, red-team gate** → [references/bid-response.md](references/bid-response.md)

## Templates and scripts

- **Templates** (`templates/`) are the fill-in-the-blank artefacts `eng-scaffold` plants, by block:
  - *core* — `CLAUDE.md.tmpl` (mode-aware: `<!--IF:block-->` fences), `project-context.md.tmpl`, `sources-README.md.tmpl`, the per-bucket source trio (`SOURCES_GO_HERE` + `reference-pack-README` + `REFERENCE_SUMMARY` + `REFERENCE_INSIGHTS`, planted once per bucket), `engagement_log.md.tmpl`, `raid_and_decisions.md.tmpl`, `source_precedence_register.md.tmpl`, `MEMORY.md.tmpl`.
  - *pursuit* — `rfp_analysis.md.tmpl`, `compliance_matrix.md.tmpl`. (`bid_research_log.md.tmpl` and `bid_response_outline.md.tmpl` stay on-demand — the research log opens when research starts, the outline only after a go decision.)
  - *delivery* — `DELIVERABLES.md.tmpl`, `FINDING_STANDARD.md.tmpl`, `findings-README.md.tmpl`, `finding.md.tmpl`, `discovery_questions.md.tmpl`.
- **Scripts** (`scripts/`):
  - `scaffold_engagement.py` — deterministic: assemble the tree from the selected blocks (`--mode`) and plant templates with placeholder substitution. Idempotent and additive.
  - `convert_source.py` — deterministic: pdf/pptx/docx/xlsx/image → markdown with `## Page N:` / `## Slide N:` / `## Sheet:` / `## Section N:` anchors + image extraction for triage.
  - `eng_lint.py` — **the mechanical gate**: bucket-leak (engagement/ cited from a bid), `[⚠VERIFY]` in a shipped artefact, unmet mandatory requirements, dangling citations, untagged/unmapped findings, dangling live-file index, unfilled spine. Run it instead of asking a reviewer to check what a script can decide.
  - `verify_scenarios.py` — self-test: scaffolds every documented mode and checks each command resolves to a playbook whose named skills and block-owned paths all exist. Run after editing a playbook, command, or the scaffolder.

## How the skills compose

- **Adopt-in-place vs greenfield.** In a brand-new repo, run `eng-scaffold` first — with the `--mode` that matches the actual work, not reflexively `full`. In an existing engagement that already follows these conventions, the in-engagement skills read the *project's own* planted convention files (e.g. `3_findings/_FINDING_STANDARD.md`), so they work without the umbrella.
- **Blocks are independent, not sequential.** No delivery skill requires `01_pursuit/` to exist, and no pursuit skill requires `02_delivery/`. Only `_sources/` + `_pm/` + `project-context.md` are shared, which is why they sit at the root rather than inside a phase.
- **The seam contract.** `eng-ingest-source` is per-document and additive and hands off an ingest report; `eng-update-canonical` is the only skill that edits the canonical summaries. `eng-write-findings` produces fact baselines; `eng-validate-findings` is the only skill that runs the corpus-wide precedence sweep; `eng-build-deliverable` consumes only validated findings.
- **Panel is a companion, not a rebuild.** `eng-scaffold` produces `.claude/project-context.md` once and then delegates to `/panel-init` (one SSOT, two consumers). Wire `panel-review` in as the mandatory gate before any deliverable ships.

## Playbooks — the standard composed workflows

Composition is **by reference, never by duplication**: a playbook is a thin checklist
that names the owning skill per step and sets the stop gates. When a task matches one
of these four recurring situations, open the playbook and run the chain:

Each playbook also has a **slash command** that just routes to it — same content, explicit entry.

| Situation | Command | Playbook | Chain |
|---|---|---|---|
| A new source doc / batch arrived | `/eng-source` | [references/playbooks/new-source-arrived.md](references/playbooks/new-source-arrived.md) | bucket → ingest → canonicalize → findings-impact → log |
| A workshop / discovery session just ended | `/eng-workshop` | [references/playbooks/post-workshop.md](references/playbooks/post-workshop.md) | held-notes → findings → canonical deltas → backlog → log |
| Findings are ready, deliverable due | `/eng-sprint` | [references/playbooks/deliverable-sprint.md](references/playbooks/deliverable-sprint.md) | validate → panel-discuss → build → panel-review → rev index |
| Day 1 of a new engagement | `/eng-new` | [references/playbooks/new-engagement.md](references/playbooks/new-engagement.md) | pick mode → scaffold → context → panel-init → first ingest batch |
| An RFP / tender arrived (bid it) | `/eng-rfp` | [references/playbooks/rfp-arrived.md](references/playbooks/rfp-arrived.md) | ingest RFP → analyse → go/no-go → research → respond → red-team |
| The scope grew — bid won, study became an engagement, client tendered | `/eng-upgrade` | [references/playbooks/adding-a-block.md](references/playbooks/adding-a-block.md) | re-scaffold with the added block → top up CLAUDE.md → write the handoff → re-baseline sources |

Anything that doesn't match a playbook: use the pipeline table above and invoke the
one stage skill that owns your task.
