# Agent memory & context discipline

How the agent-facing state stays canonical and lean across a long engagement — so the
top-level CLAUDE.md never rots into a stale dumping ground.

## Contents
- The five-file division of labour
- The anti-rot rules
- The pointer-table pattern
- Client-facing guardrails as always-apply rules
- Cross-session memory file format
- CLAUDE.md and AGENTS.md / other agents

## The five-file division of labour

| File | Role | Write cadence | Never put here |
|---|---|---|---|
| **`CLAUDE.md`** (repo root, and per-subdir if needed) | **Lean navigation index** + always-apply guardrails. Points to everything; stores almost nothing. | **Milestones only** — new phase, new deliverable, new recurring correction, navigation change | Facts that live in an SSOT file; version numbers; anything that changes weekly |
| **`.claude/project-context.md`** | **Canonical project facts** — client, scope, timeline, tech stack, stakeholders, pre-decisions, open questions. Auto-loaded by every `/panel-*` skill. | On material fact change; dated `Last updated:` header | Navigation; deliverable versions; narrative journal |
| **`DELIVERABLES.md`** | **Live-file index** — which exact file is the current version of each deliverable + "where to search / where NOT to." | Whenever a deliverable revs | Version numbers duplicated into CLAUDE.md (they rot — CLAUDE.md *points* here) |
| **`_pm/engagement_log.md`** | **Narrative journal** — per-session write-ups, findings deltas, ingestion notes. | Every working session | The lean summary (that's CLAUDE.md's "Engagement Progress") |
| **`~/.claude/projects/<slug>/memory/`** | **Cross-session auto-memory** — `MEMORY.md` flat index + one-fact-per-file entries. | When a durable lesson/preference/gotcha emerges | Transient task state; project-scoped facts that belong in the repo |

## The anti-rot rules

The whole system defends against one failure mode: **CLAUDE.md accreting stale detail.**

1. **Single source of truth, referenced not copied.** A fact lives in exactly one file;
   everything else links to it. (Deliverable versions live only in `DELIVERABLES.md`;
   CLAUDE.md refuses to name them because "the index is authoritative; version numbers rot.")
2. **Milestone-gate on CLAUDE.md.** Update it only on a phase milestone, a new deliverable, a
   new recurring correction, or a navigation change. Everything else flows to the SSOT file or
   the engagement log.
3. **Dated freshness stamps** on canonical files (`project-context.md` carries `Last updated:`)
   so staleness is visible.
4. **Memory-promotion trigger.** A lesson graduates to a memory file the moment it's a
   *recurring* correction or a fact that must survive a fresh session — not before. One fact
   per file keeps each atomically updatable and linkable.
5. **Two-tier progress log.** The compact "Engagement Progress" section in CLAUDE.md is the
   skim; the blow-by-blow goes to `engagement_log.md`. They never duplicate.

## The pointer-table pattern

CLAUDE.md's central device is a table — `Topic | Source-of-truth file | Use when`. Each row
routes the agent to the one authoritative file for a topic and says *when* to open it. This
is what converts CLAUDE.md from a knowledge store into a **router**. It is the reusable heart
of the lean-index approach.

## Client-facing guardrails as always-apply rules

Recurring corrections that must *never* be re-litigated are promoted out of per-session memory
into a top-of-CLAUDE.md **"ALWAYS apply"** block (e.g. framing rules, "no internal scaffolding
on the slide face", plain language, benchmark-universe discipline, template matching). Each
rule ends with a `→ pointer` to the memory/feedback file that spawned it. This is the bridge
between per-session memory and project-permanent doctrine.

## Cross-session memory file format

One fact per file, named `<type>_<slug>.md`, with frontmatter:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line what-and-why — used to decide relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact; for feedback/project follow with **Why:** and **How to apply:** lines.
Link related memories with [[their-name]].>
```

The four types:
- **`user`** — durable facts about the human (role, expertise, preferences, language).
- **`feedback`** — recurring corrections ("do X, never Y") — usually the largest class; include the *why*.
- **`project`** — engagement-specific facts that must survive across sessions (a reframed model, a live-file index).
- **`reference`** — reusable credentials/assets from other engagements.

`MEMORY.md` is a **flat index**: `- [Title](file.md) — one-line hook.` No frontmatter, no
nesting — it exists so the agent can scan all durable knowledge in one read. Before saving,
check for an existing file that already covers it and update that instead of duplicating.

## CLAUDE.md and AGENTS.md / other agents

`CLAUDE.md` is the Claude-specific project-instruction file; `AGENTS.md` is the cross-agent
equivalent read by other coding agents. The same lean-index discipline applies to both. If a
project needs both, keep **one** as the real index and make the other a thin pointer to it
(`See CLAUDE.md`), so you never maintain the same facts twice. The same milestone-gate,
single-source-of-truth, and pointer-table rules hold regardless of which agent reads the file.
