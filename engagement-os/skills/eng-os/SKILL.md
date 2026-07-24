---
name: eng-os
description: Use when starting or running a document-heavy consulting / advisory engagement (data strategy, assessment, target architecture, roadmap, cost model, exec summary); when you need the pipeline map, the shared conventions (finding schema, source-precedence, directory rules, memory discipline), or a composed multi-stage playbook (new source, post-workshop, deliverable sprint, new engagement); or when deciding which eng-* stage skill applies.
---

# Engagement OS

A repeatable operating model for consulting engagements that run on documents:
raw client materials come in, and defensible client deliverables go out — with a
traceable chain between them so every claim in a deck can be walked back to its source.

This skill is the **map**. It explains the pipeline and points to the one skill that
owns each stage. The deep conventions live in `references/`; the fill-in artefacts
live in `templates/`; deterministic helpers live in `scripts/`.

## The pipeline (one job per stage)

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
| **Scaffold** | `eng-scaffold` | Stand up the standard repo (folders + CLAUDE.md + project-context + DELIVERABLES + memory), then delegate to `/panel-init`. |
| **Ingest** | `eng-ingest-source` | Convert ONE client/reference document to faithful, citable markdown with lossless image/OCR handling + a manifest row. |
| **Canonicalize** | `eng-update-canonical` | Fold new facts into the canonical `00_REFERENCE_SUMMARY` (facts) and `01_REFERENCE_INSIGHTS` (interpretation), keeping provenance. |
| **Findings** | `eng-write-findings` | Turn evidence into standards-conformant current-state findings (severity/priority, evidence tags, precedence tags, backbone mapping). |
| **Validate** | `eng-validate-findings` | Provenance/validation sweep: evidence-tag audit, precedence arbitration, `[⚠VERIFY]` register, backbone + canonical alignment. |
| **Build** | `eng-build-deliverable` | Assemble an as-is / to-be deliverable from *validated* findings, provenance intact; add each deliverable's own so-what. |
| **Memory** | `eng-maintain-memory` | Keep CLAUDE.md / project-context / DELIVERABLES / cross-session memory canonical and lean (anti-rot). Runs throughout. |
| **Review** | Panel Framework (companion) | `panel-discuss` locks a deliverable's structure; `panel-review` is the hard red-line gate before anything ships; `panel-debrief` after workshops. |

## The five load-bearing principles

Everything in this pack exists to protect these. If a choice conflicts with one, the principle wins.

1. **Source → derived separation.** Originals are never edited. Every derived markdown, finding, and slide traces back to an original by path + page/slide. Provenance is a first-class citizen, not an afterthought.
2. **Single source of truth, referenced not copied.** Each fact lives in exactly one file; everything else *links* to it. Deliverable versions live only in `DELIVERABLES.md`; project facts only in `.claude/project-context.md`; CLAUDE.md is a router, never a fact store.
3. **A finding is a fact baseline, not a recommendation.** Findings record what *is* (observation and interpretation kept visibly separate) so every downstream deliverable can cite the same fact with its own so-what, without re-pasting evidence.
4. **Precedence resolves conflict; nothing is deleted.** Measured-from-the-system beats the workshop room beats the vendor deck (T1 > T2 > T3). On conflict, keep both and stamp the loser `⚠ superseded-by`. Unverifiable claims are gated with `[⚠VERIFY]`.
5. **Lean by design.** Depth lives in dedicated files; the index stays skimmable. CLAUDE.md and canonical summaries are updated on *milestones and material change*, not every edit.

## Conventions — read the reference file that matches your task

Keep these one level away; read the specific file when the stage needs it.

- **Directory + file naming + the dual-index discipline** → [references/directory-conventions.md](references/directory-conventions.md)
- **Ingestion, lossless image/OCR rule, facts-vs-insights canonical split** → [references/canonical-reference.md](references/canonical-reference.md)
- **Finding schema — severity vs priority, evidence tags, body shapes** → [references/finding-standard.md](references/finding-standard.md)
- **Source precedence (T1/T2/T3), `[⚠VERIFY]`/V-n register, conflict clusters** → [references/provenance-and-precedence.md](references/provenance-and-precedence.md)
- **As-is / to-be assembly, versioning, the panel gate** → [references/deliverable-build.md](references/deliverable-build.md)
- **CLAUDE.md / project-context / DELIVERABLES / memory discipline (incl. AGENTS.md)** → [references/memory-discipline.md](references/memory-discipline.md)

## Templates and scripts

- **Templates** (`templates/`) are the fill-in-the-blank artefacts `eng-scaffold` plants into a new repo: `CLAUDE.md.tmpl`, `project-context.md.tmpl`, `DELIVERABLES.md.tmpl`, `FINDING_STANDARD.md.tmpl`, `findings-README.md.tmpl`, the `_md/` reference-pack trio, `engagement_log.md.tmpl`, `source_precedence_register.md.tmpl`, `discovery_questions.md.tmpl`, `finding.md.tmpl`, `MEMORY.md.tmpl`.
- **Scripts** (`scripts/`):
  - `scaffold_engagement.py` — deterministic: create the folder tree and plant templates with placeholder substitution.
  - `convert_source.py` — deterministic: pdf/pptx/docx/xlsx/image → markdown with `## Page N:` / `## Slide N:` anchors + image extraction for triage.

## How the skills compose

- **Adopt-in-place vs greenfield.** In a brand-new repo, run `eng-scaffold` first. In an existing engagement that already follows these conventions, the in-engagement skills read the *project's own* planted convention files (e.g. `3_findings/_FINDING_STANDARD.md`), so they work without the umbrella.
- **The seam contract.** `eng-ingest-source` is per-document and additive and hands off an ingest report; `eng-update-canonical` is the only skill that edits the canonical summaries. `eng-write-findings` produces fact baselines; `eng-validate-findings` is the only skill that runs the corpus-wide precedence sweep; `eng-build-deliverable` consumes only validated findings.
- **Panel is a companion, not a rebuild.** `eng-scaffold` produces `.claude/project-context.md` once and then delegates to `/panel-init` (one SSOT, two consumers). Wire `panel-review` in as the mandatory gate before any deliverable ships.

## Playbooks — the standard composed workflows

Composition is **by reference, never by duplication**: a playbook is a thin checklist
that names the owning skill per step and sets the stop gates. When a task matches one
of these four recurring situations, open the playbook and run the chain:

| Situation | Playbook | Chain |
|---|---|---|
| A new source doc / batch arrived | [references/playbooks/new-source-arrived.md](references/playbooks/new-source-arrived.md) | ingest → canonicalize → findings-impact → log |
| A workshop / discovery session just ended | [references/playbooks/post-workshop.md](references/playbooks/post-workshop.md) | held-notes → findings → canonical deltas → backlog → log |
| Findings are ready, deliverable due | [references/playbooks/deliverable-sprint.md](references/playbooks/deliverable-sprint.md) | validate → panel-discuss → build → panel-review → rev index |
| Day 1 of a new engagement | [references/playbooks/new-engagement.md](references/playbooks/new-engagement.md) | scaffold → context → panel-init → first ingest batch |

Anything that doesn't match a playbook: use the pipeline table above and invoke the
one stage skill that owns your task.
