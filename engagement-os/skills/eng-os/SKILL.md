---
name: eng-os
description: Use when running a document-heavy consulting / advisory engagement across both the pursuit/bid side (analyse an RFP, research, write a tender response) and the delivery side (assessment, target architecture, roadmap, cost model, exec summary); when you need the pipeline map, the shared conventions (finding schema, source-precedence, directory rules, memory discipline), or a composed multi-stage playbook (new source, post-workshop, deliverable sprint, new engagement, RFP-arrived); or when deciding which eng-* stage skill applies. (Starting a repo from scratch is `eng-scaffold` — this skill is the map, not the shovel.)
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

## Standalone research — the short route

When the task is **sources in → evidence-based report or deck out**, with no RFP and no delivery
programme, use the composed route rather than invoking stage skills one by one:

```text
/eng-new <topic>, research only
  → approve the drafted question spine
/eng-source <files-or-folder>      repeat per source batch
/eng-sprint the research output
  → choose Markdown, Word/PDF, PowerPoint, or workbook
```

Default repo name: `research-<project-slug>`. The question list in `00_research/README.md` is
locked before ingest; sourced facts and interpretations are canonicalised by bucket; our analysis
goes in `00_research/1_analysis/`; reviewed output goes in `00_research/2_output/`. `/eng-sprint`
owns validation, structure, build, review, live-index update and the final format question.

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
| **Change impact** | `eng-propagate-change` | Detect manual edits since the last reconciled checkpoint, refresh deterministic projections through their owning skills, and reopen only affected review. Cross-cutting across every lane. |
| **Review** | Panel Framework (companion) | `panel-discuss` locks a deliverable's structure; `panel-review` is the hard red-line gate before anything ships; `panel-debrief` after workshops. |

## The pursuit pipeline (bid side — win the work first)

Before delivery there's the bid. Same document-and-provenance discipline, aimed at a compliant,
winning tender. Runs in `01_pursuit/<ENG-ID>/`, sourced from `_sources/pre_award/` + `_sources/public/`.

```
ingest RFP ─► index assets ─► analyse ─► research gaps ─► write response ─► R1 panel red-team
                                  │  │                          │            ─► R2 human ─► check ─► submit
                                  │  └── estimate (scope → effort → price)
                                  └── clarifications (dimension sweep → panel lens → human sends)
```

| Stage | Skill | What it does |
|---|---|---|
| **Index assets** | `eng-index-assets` | Turn our own reusable material into something a bid can cite: what each asset **proves**, dated, in-window against this tender's recency rule, with its permission constraints — plus the gaps we cannot evidence. Decides which matrix rows are genuinely `gap`. |
| **Analyse** | `eng-rfp-analyze` | Decompose the RFP: source coverage audit, requirement/compliance matrix, **scope decomposition + volumetric baseline**, understanding-and-solution read, evaluation map, win-themes, risks/escalations and materials-needed. |
| **Estimate** | `eng-estimate` | Turn the scope decomposition into a bottom-up effort model with an overlap audit, a P50/P80 range kept separate from scope-variance scenarios, the client-side hours ask, and the price-vs-marks decision table. Maintains a **formula-live workbook** plus its generated markdown snapshot. Priced tenders only — and it needs §3 of the analysis to exist. |
| **Research** | `eng-bid-research` | Close the analysis gaps with comprehensive, cited, zero-fabrication research (external `[T3:OWN]` + firm-held uploads). |
| **Respond** | `eng-bid-respond` | Assemble the response from the matrix, matching the RFP's mandated format; compliance-first, proof-backed win-themes, every claim traceable. One markdown file per section, each carrying its own review status through **two rounds** — R1 panel red-team (does it score?), R2 experienced human. |
| **Check** | `eng-check` | Run every mechanical gate that applies and report what is blocking, grouped by what the user must do. Runs throughout, not only before submission — nobody should type a script path to reach a gate. |
| **Propagate change** | `eng-propagate-change` | Hash the reconciled dependency graph, detect edited R/S/A/BR/F inputs and maintained files, refresh deterministic outputs through existing skills, reopen affected review, and leave frozen packages immutable. |

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
- **Deck round trip — splice corrected slides back in, then verify the package** → [references/deck-assembly.md](references/deck-assembly.md)
- **CLAUDE.md / project-context / DELIVERABLES / memory discipline (incl. AGENTS.md)** → [references/memory-discipline.md](references/memory-discipline.md)
- **Guided elicitation — how to fill an artefact WITH the user instead of handing them a blank** → [references/guided-elicitation.md](references/guided-elicitation.md)
- **RFP decomposition — source coverage, compliance matrix, scope, solution, evaluation map, win-themes and risks** → [references/rfp-analysis.md](references/rfp-analysis.md)
- **Estimation — scope → effort → cost → price, two techniques, client-side hours, price-vs-marks** → [references/estimation.md](references/estimation.md)
- **Bid research — depth+breadth, source discipline, zero-fabrication, the [⚠VERIFY] gate** → [references/bid-research.md](references/bid-research.md)
- **Bid response — requirement-driven assembly, format-match, traceability, red-team gate** → [references/bid-response.md](references/bid-response.md)
- **Clarification questions — derived by dimension sweep, panel lens, human sends** → [references/rfp-analysis.md](references/rfp-analysis.md) §Step 6b

## Templates and scripts

- **Templates** (`templates/`) are the fill-in-the-blank artefacts `eng-scaffold` plants, by block:
  - *core* — `CLAUDE.md.tmpl` (mode-aware: `<!--IF:block-->` fences), `project-context.md.tmpl`, `sources-README.md.tmpl`, the per-bucket source trio (`SOURCES_GO_HERE` + `reference-pack-README` + `REFERENCE_SUMMARY` + `REFERENCE_INSIGHTS`, planted once per bucket), `engagement_log.md.tmpl`, `raid_and_decisions.md.tmpl`, `source_precedence_register.md.tmpl`, `MEMORY.md.tmpl`.
  - *pursuit* — `rfp_analysis.md.tmpl`, `compliance_matrix.md.tmpl`, `clarification_log.md.tmpl` (the query deadline lands before the submission deadline, so this one is needed from day 1). On demand — **created because the condition held, never because the list names it**: `estimation.md.tmpl` (the tender is priced), `bid_reuse_analysis.md.tmpl` (a prior bid exists — **check whether one does before drafting, and record the negative when it doesn't**), `bid_research_log.md.tmpl`, `bid_response_outline.md.tmpl`.
  - *delivery* — `DELIVERABLES.md.tmpl`, `FINDING_STANDARD.md.tmpl`, `findings-README.md.tmpl`, `finding.md.tmpl`, `discovery_questions.md.tmpl`.
- **Scripts** (`scripts/`) are agent-only engines, never user entry points. Users invoke skills
  and commands in natural language; do not relay a Python command or CLI flags unless they
  explicitly ask about implementation. **Reuse before building.** Where a capability already has a skill —
  `xlsx`, `docx`, `pptx`, `pdf` — these scripts *call* it rather than reimplement it, and own only
  the packaging the pack's discipline needs and no general tool provides: provenance headers,
  citable anchors, the estimation formula graph, the deliverable gates. Extraction goes through
  `pandoc` / `markitdown`; spreadsheet recalculation and model conventions come from the `xlsx`
  skill; OOXML schema validation is the `pptx` skill's `office/validate.py`; `soffice` is invoked
  through the office skills' wrapper, because bare `soffice` hangs in sandboxes. A script here
  that starts re-teaching one of those skills is a bug.
  - `scaffold_engagement.py` — deterministic: assemble the tree from the selected blocks (`--mode`) and plant templates with placeholder substitution. Idempotent and additive.
  - `convert_source.py` — deterministic: pdf/pptx/docx/xlsx/image → markdown with `## Page N:` / `## Slide N:` / `## Sheet:` / `## Section N:` anchors + image extraction for triage. `--scan <root>` answers "what arrived that I haven't ingested?" by diffing source files against their `_md/` outputs — so nobody types a path for a file already in the tree.
  - `triage_images.py` — the executor for the step after conversion. `--worklist` gathers what a vision pass needs to judge an extracted image (unit, dimensions, size, OCR hint, surrounding markdown); `--apply` writes the verdicts back — deleting a decorative file with its inline block and index line, captioning a kept one, parking OCR text — and records a ledger. It **does not classify**: 34 images in one deck and 296 in another is why the judgment is batched to vision agents, and why a reasonless bulk `[decorative]` is refused. Method: [references/image-triage.md](references/image-triage.md).
  - `build_estimate_workbook.py` — private deterministic engine behind **`eng-estimate`**, never a user entry point. It seeds and refreshes the **formula-live** `.xlsx` + generated markdown snapshot: rate card → grade lookup → effort → P50/P80 → cost base → the price/marks decision table. Every derived cell is a real formula so a reviewer can move an input and watch it recalculate.
  - `change_impact.py` — private deterministic engine behind **`eng-propagate-change`**. Records hash-only reconciled checkpoints, maps changed R/S/A/BR/F dependencies to affected sections, mechanically invalidates stale review, and rejects direct edits to generated or frozen outputs. It orchestrates existing skills; it does not edit Excel/Word/PPT itself.
  - `check_companions.py` — answers "is anything I delegate to actually missing, or can I skip
    the install?". Resolves each companion across all four layouts a skill can live in (personal,
    skills-dir, versioned plugin cache, marketplace clone), states what its absence costs, and
    prints install commands only for what is absent. `engagement-os` declares **no** manifest
    `dependencies` on purpose: an unresolvable dependency disables the dependent plugin, so a
    hard declaration would trade "cannot recalculate a workbook" for "the pack is dead". The
    install-everything path is the separate `consulting-suite` bundle; the skip path is
    installing `engagement-os` alone. Reached through `eng-check companions`, never by path.
  - `eng_lint.py` — **the mechanical gate**. The rule set is the registry (`RULES`); read it with `python3 eng_lint.py --list` rather than trusting any prose copy — including this one. Rules have clean/violated fixtures in `tests/run_tests.py`; the stateful change-impact rule is exercised in `tests/test_change_impact.py`. Lint exists so nobody asks a reviewer to check what a script can decide.
  - `section_contract.py` — machine form of `references/section-contract.md`: the status vocabulary, frontmatter fields, and id syntax that lint and `render_document.py` both import. Change doc and module in the same commit.
  - `figure_contract.py` — the same idea for the figure block: the tags, accounting lines and patterns that `convert_source.py` writes, `triage_images.py` rewrites and `eng_lint.py` counts. All three used to carry private copies of the same literals, so renaming the caption stub in one left the others matching a pattern that no longer occurred — `--apply` rewrote nothing and reported success. Change `references/image-triage.md` and this module in the same commit; `tests/run_tests.py` round-trips real converter output through all three.
  - `render_document.py` — the render engine behind the **`eng-render`** skill (sections → docx/pdf via a pandoc reference.docx, or a deck manifest for `presentation-builder`). It lives here because eng-lint and the scaffolder are its siblings; `eng-render` is the skill facade and declares the dependency.
  - `verify_deck.py` — **the mechanical gate on an assembled `.pptx`**, reading the OOXML with stdlib zipfile. Catches what a build log cannot show: a flattened picture-per-slide deck, a font neither standard nor embedded, a miscounted splice, a figure whose image did not come across. Assembly itself belongs to the `pptx` skill — see [references/deck-assembly.md](references/deck-assembly.md). Fixtures in `tests/test_verify_deck.py`.
  - `verify_scenarios.py` — self-test: scaffolds every documented mode, asserts the fresh tree lints with zero errors, and checks each command's targets resolve, every named skill exists, and every block-owned path exists (unknown top-level-looking paths fail — a typo is not allowed to pass silently). Run after editing a playbook, command, or the scaffolder.

## How the skills compose

- **Adopt-in-place vs greenfield.** In a brand-new repo, run `eng-scaffold` first — with the `--mode` that matches the actual work, not reflexively `full`. In an existing engagement that already follows these conventions, the in-engagement skills read the *project's own* planted convention files (e.g. `3_findings/_FINDING_STANDARD.md`), so they work without the umbrella.
- **Blocks are independent, not sequential.** No delivery skill requires `01_pursuit/` to exist, and no pursuit skill requires `02_delivery/`. Only `_sources/` + `_pm/` + `project-context.md` are shared, which is why they sit at the root rather than inside a phase.
- **The seam contract.** `eng-ingest-source` is per-document and additive and hands off an ingest report; `eng-update-canonical` is the only skill that edits the canonical summaries. `eng-write-findings` produces fact baselines; `eng-validate-findings` is the only skill that runs the corpus-wide precedence sweep; `eng-build-deliverable` consumes only validated findings.
- **Panel is a companion, not a rebuild.** `eng-scaffold` produces `.claude/project-context.md` once and then delegates to `/panel-init` (one SSOT, two consumers). Wire `panel-review` in as the mandatory gate before any deliverable ships.

## Playbooks — the standard composed workflows

Composition is **by reference, never by duplication**: a playbook is a thin checklist
that names the owning skill per step and sets the stop gates. When a task matches one
of these recurring situations, open the playbook and run the chain:

Each playbook also has a **slash command** that just routes to it — same content, explicit entry.

| Situation | Command | Playbook | Chain |
|---|---|---|---|
| A new source doc / batch arrived | `/eng-source` | [references/playbooks/new-source-arrived.md](references/playbooks/new-source-arrived.md) | bucket → ingest → canonicalize → findings-impact → log |
| A workshop / discovery session just ended | `/eng-workshop` | [references/playbooks/post-workshop.md](references/playbooks/post-workshop.md) | held-notes → findings → canonical deltas → backlog → log |
| Findings or research analysis are ready, deliverable due | `/eng-sprint` | [references/playbooks/deliverable-sprint.md](references/playbooks/deliverable-sprint.md) | validate → panel-discuss → build → panel-review → rev index → choose format |
| Day 1 of a new engagement | `/eng-new` | [references/playbooks/new-engagement.md](references/playbooks/new-engagement.md) | pick mode → scaffold → context → panel-init → first ingest batch |
| An RFP / tender arrived (bid it) | `/eng-rfp` | [references/playbooks/rfp-arrived.md](references/playbooks/rfp-arrived.md) | ingest RFP → analyse → research → respond → red-team |
| The scope grew — bid won, study became an engagement, client tendered | `/eng-upgrade` | [references/playbooks/adding-a-block.md](references/playbooks/adding-a-block.md) | re-scaffold with the added block → top up CLAUDE.md → write the handoff → re-baseline sources |
| A reviewer changed an existing artefact | `/engagement-os:eng-propagate-change` | skill-owned workflow | scan → invalidate affected review → invoke owning skills → re-render/version if needed → checkpoint |

Anything that doesn't match a playbook: use the pipeline table above and invoke the
one stage skill that owns your task.
