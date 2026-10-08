---
name: panel-discuss
description: Convene a panel of roles to discuss a topic. v2 native-agents architecture — Recon Index + Evidence Bundle + parallel native Task dispatch. Supports 6 goal types (brainstorm, decision, alignment, problem-solving, discovery, requirements-gathering). Mode B round 2 cross-influence on by default. Use when the user asks to "discuss", "talk through", "get X's view on", wants "multiple perspectives", or says things like "run a panel", "brainstorm with the team", "make this a group decision", "what would the architect + PM + security say".
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task", "Agent", "Skill"]
argument-hint: "\"<topic>\" [--goal=<type>] [--roles=<role1,role2>]"
---

# /panel-discuss — Panel discussion (v2)

## Overview

Runs a multi-role panel discussion using the orchestrator-loads-unified-context
pattern per v2 spec §3. The skill (main thread) owns Recon, Bundle, dispatch,
and synthesis. Each role speaks via a native Claude Code subagent dispatched
through the `Task` tool.

## Root conventions

Before any other work, run the shared root resolver to learn both
`project_root` and `plugin_root`:

```bash
bash "${CLAUDE_SKILL_DIR}/../../framework-scripts/resolve-roots.sh"
```

The resolver prints `project_root=<abs>` (the nearest ancestor of `$PWD`
containing `.claude/` or `.git/`) and `plugin_root=<abs>` (the installed
panel-framework plugin root). For the full contract — which assets belong
to the plugin vs the user's project, hard rules, and failure semantics —
follow `<plugin_root>/framework-scripts/root-conventions.md`. Treat resolver
output as authoritative; never guess.

## When to invoke

- The user asks to "discuss", "talk through", "get X's view on" a topic.
- The user wants stakeholder reasoning applied to a problem.
- The user wants to hear multiple perspectives before deciding.

If the request is closer to "review this document" → point to `/panel-review`
(Plan 2). If closer to "draft this section" → `/panel-draft` (Plan 2). If
"meeting debrief" → `/panel-debrief` (Plan 2).

## Inputs

| Input | Required | Default / behavior if absent |
|-------|----------|-------------------------------|
| topic | yes | Ask the user |
| goal_type | yes | Ask — one of: brainstorm, decision, alignment, problem-solving, discovery, requirements-gathering |
| roles | no | Propose a relevant set, user confirms. Continuation: `+role` adds, `-role` removes, bare list replaces |
| mode | — | Mode B only (v2 dropped Mode A) |
| continue (thread_id) | no | Start new thread |

CLI flags:
- `--no-recon` — skip Recon + Bundle, dispatch with project-context only
- `--recon-only` — run Recon, present, stop (debugging)
- `--force-dig` — every role must Read ≥1 bundle entry
- `--no-convergence` — skip Mode B round 2
- `--max-bundle-tokens=<N>` — override budget
- `--keywords=<list>` — override keyword extraction
- `--context=<path>[,<path>...]` — force-include paths in bundle
- `--no-log` — skip log write

## Automation mode

- If topic + goal type + role set are already clear in the current user turn,
  proceed directly. Do not ask a redundant confirmation question.
- If a required input is missing in a non-interactive run, emit a concise
  `Missing inputs:` checklist and stop instead of starting an interview.
- If `recon.confirm_with_user: false`, still show the Recon / Bundle summary,
  but treat it as pre-approved and continue without waiting for a reply.

## Step-by-step

### Step 1: Parse intent

Extract topic, goal_type, roles, continue, flags. For anything required but
missing (topic, goal_type), ask in one numbered list. Do not guess goal_type.
If the run is non-interactive, emit the missing-input checklist and stop.

### Step 2: Validate and load

- Run the root resolver script first and cache the returned absolute
  `project_root` and `plugin_root`.
- Validate goal_type against the 6 allowed values.
- Read `<project_root>/.claude/panel-config.yaml`. Only if missing, fall back
  to `<plugin_root>/panel-config.default.yaml`.
- Read `<project_root>/.claude/project-context.md` — if missing, direct user to
  `/panel-init`.
- For each resolved role, verify agent exists at
  `<project_root>/.claude/agents/panel-<role>.md` (project override) or
  `<plugin_root>/agents/panel-<role>.md` (plugin default). If missing, suggest
  best match or `/panel-new-role`.

### Step 3: Determine thread_id and resolve output path

```
thread_id =
  if --continue=<id> given: that id
  else: "<topic-slug>-<YYYY-MM-DD>" (append -2, -3 ... on collision)
```

Resolve output path:

```bash
bash <plugin_root>/framework-scripts/resolve-output-path.sh \
  --project-root <repo-root> \
  --skill discuss \
  --thread-id <thread_id>
```

### Step 4: Recon Index

If `--no-recon` flag passed, skip to Step 6 with empty bundle.

Otherwise, load and follow
`<plugin_root>/skills/_shared/prompts/recon-system.md`.
Present the Recon Index (full candidate list, no truncation). If
`recon.confirm_with_user: true`, get user approval. Otherwise, record that the
Recon shortlist was auto-approved and continue.

### Step 5: Evidence Bundle

Load and follow
`<plugin_root>/skills/_shared/prompts/bundle-system.md`. Build the bundle.
Present summary. If `recon.confirm_with_user: true`, get user approval.
Otherwise, record that the bundle was auto-approved and continue.

PDF uses native Read. xlsx / docx / pptx are converted via their respective
Claude Code skills (see bundle-system.md "Conversion invocation pattern").
Conversions cache at `panel/_recon_cache/<thread_id>/` and are reused across
`--continue` calls on the same thread.

### Step 6: Dispatch roles in parallel

Load the dispatch base prompt:
`<plugin_root>/skills/panel-discuss/prompts/role-dispatch-base.md`.
Load the goal-type dispatch prompt:
`<plugin_root>/skills/panel-discuss/prompts/goal-type-<goal_type>.md`.

For each role, compose a dispatch prompt by concatenating:

1. The base prompt, with placeholders replaced:
   - `<<<PROJECT_CONTEXT>>>` — full content of `.claude/project-context.md`
   - `<<<EVIDENCE_BUNDLE>>>` — the bundle from Step 5 (or "(Recon skipped)")
   - `<<<TOPIC>>>` — user's topic
   - `<<<GOAL_TYPE>>>` — goal type name
   - `<<<OTHER_ROLES>>>` — comma-separated list of other roles in the panel
   - `<<<PRIOR_ROUNDS>>>` — prior round content if `--continue`, else "(none — new thread)"
2. The goal-type prompt
3. A role-specific suffix:
   ```
   **Your role:** panel-<role-name>
   **This is round 1** of the discussion.
   ```

**Dispatch all roles in ONE assistant message** by making N `Task` calls
in parallel. This is the documented Claude Code pattern for parallel
subagent execution. (Some harness versions alias the tool as `Agent`;
both are listed in `allowed-tools` for compatibility, but all examples
and prose in this skill use the canonical `Task` name.)

Example (3 roles):

```
Task(subagent_type="panel-solution-architect",
     description="Solution Architect on <topic>",
     prompt=<composed prompt>)
Task(subagent_type="panel-security-lead",
     description="Security Lead on <topic>",
     prompt=<composed prompt>)
Task(subagent_type="panel-finance-lead",
     description="Finance Lead on <topic>",
     prompt=<composed prompt>)
```

Await all responses. If a role's dispatch fails (F8), continue with remaining
roles and note the failure in synthesis.

### Step 7: Mode B round 2 (convergence) — default on

If `mode_b_convergence: true` AND `--no-convergence` NOT passed:

For each role, compose a round-2 prompt. **Keep the shared prefix identical**
to round 1 (cache benefit). The differences are in `<<<PRIOR_ROUNDS>>>`:

```
## Round 1 — All Contributions

**[panel-<role1>]**
<role1 round 1 output>

**[panel-<role2>]**
<role2 round 1 output>
...
```

And in the role-specific suffix:

```
**Your role:** panel-<role-name>
**This is round 2.** You have all other roles' Round 1 positions above.

Now that you've heard them, what updates your view? Respond in this format:

**Status:** unchanged | shifted | additional concern
**Updated position (if any):** <new position or "same as round 1">
**What changed it (cite which role's point, if applicable):** <role name + their point>
_Consulted: ..._
```

Dispatch all roles in parallel (one message, N Task calls).

### Step 8: Synthesize

Load `<plugin_root>/skills/panel-discuss/prompts/synthesis-<goal_type>.md`.
Follow the output structure for the goal type. Also emit, for all goal types:

```markdown
## 🔁 Recommended Next Round

<Include IF consensus not reached OR a clearly-missing role emerged OR a
material unknown blocks progress.>

Why another round is needed:
- <reason>

Suggested additions:
- <role-name> — <one-line rationale>

Suggested continuation:
/panel-discuss ... --continue=<thread_id> --roles=+<new-role>
```

Or, if complete:

```markdown
## ✅ No further rounds recommended — discussion is complete.
```

And:

```markdown
## 📎 Suggested follow-ups

<Include bullets that apply:>
- Produced a decision → draft the write-up: `/panel-draft "<section>" --roles=<most-relevant-role>` (Plan 2)
- Decision needs scrutiny → `/panel-review <draft path> --roles=<3-5 reviewers>` (Plan 2)
- Missing role identified → `/panel-new-role "<description>"` (Plan 3)
```

### Step 9: Emit

Header:

```markdown
# 🎙 Panel Discussion — <topic>

**Goal:** <goal_type> | **Thread:** <thread_id>
**Participants:**
- panel-<role1>
- panel-<role2>

---
```

Then: bundle summary (1 paragraph), round 1 contributions, round 2 (if run),
synthesis. Append observability footer with **Recon Diagnostics** (required
even when all-green):

```markdown
---
_Skill: /panel-discuss | Goal: <goal_type> | Panel: <roles> | Thread: <thread_id> | Out: <source-from-resolver>_

## 📎 Recon Diagnostics
- Keywords used: [<list>]
- Candidates found: <N> (<M> truncated by head_limit)
- Files consulted by roles: <X> / <Y> approved
- Read failures: <count> (details above in Evidence Bundle)
- Web fallbacks: <count>
- Oversized files skipped: <count>
- Binary conversion failures: <count>
```

If `--no-log` → skip file write, tell user "Log write skipped (--no-log)".

## Self-check before emitting

- [ ] goal_type was explicitly confirmed (not silently substituted)
- [ ] Recon Index was presented to user (unless `--no-recon`) and approved
- [ ] Evidence Bundle summary was shown and approved
- [ ] Each participating role produced ≥1 contribution
- [ ] Each contribution includes `_Consulted:` line
- [ ] **Grounding check** — if bundle non-empty, >50% of roles cite ≥1 `[E-id]`.
  - If NOT: refuse to emit, warn: "N of M roles spoke, <k> cited evidence, but Y files are in the bundle. This is the abstract-output failure mode. Options: re-run with `--force-dig` / narrow topic / expand role set."
- [ ] Synthesis matches the goal-type output structure
- [ ] Either "Recommended Next Round" or "No further rounds recommended" appears
- [ ] Observability footer includes Recon Diagnostics block
- [ ] Log written to resolved path (unless `--no-log`)

If any item fails, fix before emitting.

## What this skill does NOT do

- Cross-thread similarity recommendation (spec §11, deferred)
- Multi-language output (v2 is en-US only)
