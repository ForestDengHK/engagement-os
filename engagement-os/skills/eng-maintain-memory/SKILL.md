---
name: eng-maintain-memory
description: Use when a recurring correction emerges, a project-context fact (stack, stakeholder, scope, pre-decision) shifts, a deliverable revs, a phase closes, CLAUDE.md is drifting stale, or the user says "update CLAUDE.md / AGENTS.md", "record this as a memory", "re-index the deliverables", or "log this milestone". Owns CLAUDE.md / `.claude/project-context.md` / `DELIVERABLES.md` / `_pm/` — the `_sources/` canonical summaries (00_REFERENCE_SUMMARY/01_REFERENCE_INSIGHTS) belong to eng-update-canonical, not here.
---

# Maintaining engagement memory

Route each kind of durable state to the one file that owns it, and keep the top-level index lean.
Method rationale + the five-file division of labour: `eng-os` → `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/memory-discipline.md`.

**If missing:** the owning file for the change doesn't exist (no CLAUDE.md /
`.claude/project-context.md` / `DELIVERABLES.md` in this repo) → the repo hasn't been
scaffolded; run `eng-scaffold` first rather than creating memory files by hand.

## Route by what changed

| What changed | Write to | Not to |
|---|---|---|
| A recurring correction / preference / gotcha | a cross-session memory file (`<type>_<slug>.md`) + `MEMORY.md` index | CLAUDE.md body |
| A canonical project fact (stack, stakeholder, scope, pre-decision) | `.claude/project-context.md` (bump `Last updated:`) | CLAUDE.md |
| A deliverable version | `DELIVERABLES.md` | CLAUDE.md (it points here) |
| A working-session detail | `_pm/engagement_log.md` (full narrative) | CLAUDE.md |
| A risk / assumption / issue / dependency, or a closed decision | `_pm/raid_and_decisions.md` (RAID tables / Decision Log) | CLAUDE.md |
| A phase/week milestone | CLAUDE.md "Engagement Progress" (one compact line) + the log | — |
| Navigation / a new SSOT file | CLAUDE.md pointer table | anywhere else |

## Operations

**Record a memory.** Classify type (`user` / `feedback` / `project` / `reference`). Write
`<type>_<slug>.md` with frontmatter (`name`, `description`, `metadata.type`) + the fact + a
`**Why:**` and `**How to apply:**` for feedback/project + `[[wikilinks]]` to related memories.
Append one line to `MEMORY.md` (`- [Title](file.md) — hook`). Check for an existing file that
already covers it and update that instead of duplicating.

**Promote a client-facing rule.** If a recurring correction is a *client-facing* rule, also add
it to CLAUDE.md's top **"ALWAYS apply"** block with a `→ pointer` to its feedback file — this is
the bridge from per-session memory to project-permanent doctrine.

**Re-index deliverables.** Rewrite `DELIVERABLES.md` current-version rows and re-assert the
"where NOT to search" exclusion list (`_deck_build/`, `*_SKELETON.*`, `archived/`, `slide_redesign/`).

**Log a milestone.** Full narrative → `engagement_log.md`; a compact one-liner → CLAUDE.md
"Engagement Progress" **only** if it's a phase/week milestone.

**Log a risk / decision.** A new risk / assumption / issue / dependency → the matching RAID
table in `_pm/raid_and_decisions.md`; a *closed* decision → the Decision Log (with rationale +
who made it + what it supersedes). Findings and deliverables cite decisions by `DEC-n` ID so a
choice is never silently re-litigated.

**Anti-rot audit** (`claude-md-prune`). Scan CLAUDE.md for: hardcoded version numbers (→ replace
with a pointer to `DELIVERABLES.md`), facts duplicated from an SSOT file, dead links, and
oversized sections that should be extracted to a dedicated file. Report + fix.

## CLAUDE.md vs AGENTS.md
`CLAUDE.md` is the Claude-specific index; `AGENTS.md` is the cross-agent equivalent. Same
lean-index discipline. If both exist, keep one as the real index and make the other a thin
pointer to it — never maintain the same facts in two files.

## Invariants
One fact = one file. CLAUDE.md never stores a rot-prone value. Every canonical file carries a
freshness stamp. Recurring corrections get promoted to always-apply doctrine with provenance.
Update CLAUDE.md on milestones, not every edit.
