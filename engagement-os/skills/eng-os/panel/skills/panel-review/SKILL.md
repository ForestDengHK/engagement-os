---
name: panel-review
description: Multi-role review of a document. Each reviewer critiques from their priorities, red_lines, operating_principles, and reference_frameworks. Red_lines are auto-flagged against document content; Operating-Principle soft conflicts are surfaced too. `--focus=<area>` narrows the critique (quality / completeness / risk / compliance / all). Use when the user asks to "review", "critique", "challenge this draft", wants "X's take on my document", says "red-line check", "security review of <path>", or "what would the architect flag here".
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task", "Agent", "Skill"]
argument-hint: "<path|inline> [--roles=<role1,role2>] [--focus=<area>]"
---

# /panel-review — Multi-role review (v2)

## Overview

v2 native-agents review. Same 5-phase pipeline as panel-discuss (Recon → Bundle
→ parallel dispatch → optional round 2 → synthesis), specialized for document
critique. Each reviewer is a native Claude Code subagent.

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

- User has a document to review from multiple perspectives
- Before shipping a client deliverable
- After `/panel-draft`, as an auto-offered follow-up

## Inputs

| Input | Required | Default |
|-------|----------|---------|
| document | yes | Ask — path or inline content |
| roles | no | Propose 3–5 based on document content + project context |
| focus | no | `all` — one of `quality | completeness | risk | compliance | all` |
| continue (thread_id) | no | New thread |

Flags: `--no-recon`, `--recon-only`, `--force-dig`, `--no-convergence`, `--max-bundle-tokens=<N>`, `--keywords=<list>`, `--context=<paths>`, `--no-log`.

## Automation mode

- If document path / inline content + focus + reviewers are already clear,
  proceed directly.
- If the required `document` input is missing in a non-interactive run, emit a
  `Missing inputs:` checklist and stop instead of starting a back-and-forth.
- If `recon.confirm_with_user: false`, treat Recon and Bundle as pre-approved
  after showing the summary.

## Step-by-step

### Step 1: Parse intent

Extract document path / inline content, roles, focus, continue, flags.
If `document` is still missing and the run is non-interactive, emit the
missing-input checklist and stop.

### Step 2: Load document

- If `document` is a path, read it fully. **Do NOT truncate.** For documents
  ≥20K characters, either (a) ask which sections to review, or (b) review
  section-by-section and aggregate findings. Truncating risks missing red-line
  violations.
- If inline, use the inline content.

### Step 3: Load context

Run the root resolver script first and cache the returned absolute
`project_root` and `plugin_root`. Read
`<project_root>/.claude/panel-config.yaml` (fallback:
`<plugin_root>/panel-config.default.yaml`) and
`<project_root>/.claude/project-context.md`. For each reviewer, verify the
agent exists at `<project_root>/.claude/agents/panel-<role>.md` or
`<plugin_root>/agents/panel-<role>.md`.

### Step 4: Determine thread_id + output path

```
thread_id = if --continue=<id> given: that id
            else: "<document-basename-slug>-<YYYY-MM-DD>" (suffix on collision)
```

Call
`<plugin_root>/framework-scripts/resolve-output-path.sh --skill review --thread-id <id>`.

### Step 5: Recon Index

If `--no-recon`, skip to Step 7. Otherwise load and follow
`<plugin_root>/skills/_shared/prompts/recon-system.md` — the Recon logic
is identical across activity skills. Seed keyword pool from the document's
content (not a separately-stated topic). Present candidates. If
`recon.confirm_with_user: true`, get user approval. Otherwise, auto-approve and
continue.

### Step 6: Evidence Bundle

Load and follow
`<plugin_root>/skills/_shared/prompts/bundle-system.md`. Build bundle,
present summary, and either get approval or auto-approve when
`recon.confirm_with_user: false`. PDF via Read, xlsx/docx/pptx via Skill-tool
invocation to the corresponding format skill.

### Step 7: Red-line pre-pass + Operating-Principle check

**Red-line checking is judgment, not regex.** For each reviewer's Red Lines:

1. For each red line, reason whether the document violates it. A violation is:
   - The document makes a claim contradicting the red line, OR
   - The document omits something the red line requires, OR
   - A required section is missing
2. Flag violations with:
   - Red line text, source reviewer role, location (line / section)
   - Severity: `critical` (hard violation), `major` (partial), `minor` (gap)
3. Collect into `redline_violations` list.

**Operating Principles soft check:** For each reviewer's Operating Principles,
identify places the document contradicts the principle (e.g., a decision
without trade-offs when the principle is "trade-offs must be written down").
Severity typically `major` or `minor`. Collect into `principle_conflicts`.

### Step 8: Dispatch reviewers in parallel

Load `<plugin_root>/skills/panel-review/prompts/reviewer-dispatch-base.md`. For
each reviewer, compose a prompt by concatenating:

1. Base prompt with placeholders:
   - `<<<PROJECT_CONTEXT>>>` — `.claude/project-context.md` content
   - `<<<DOCUMENT_PATH>>>` — the path (or "(inline)")
   - `<<<FOCUS>>>` — focus value
   - `<<<DOCUMENT_CONTENT>>>` — full document text
   - `<<<EVIDENCE_BUNDLE>>>` — bundle from Step 6 (or "(Recon skipped)")
   - `<<<REDLINE_VIOLATIONS>>>` — this reviewer's red-line pre-pass findings
   - `<<<PRINCIPLE_CONFLICTS>>>` — this reviewer's operating-principle findings
   - `<<<OTHER_ROLES>>>` — comma-separated other reviewers
2. `<plugin_root>/skills/panel-review/prompts/review-output-format.md`
3. Role-specific suffix:
   ```
   **Your role:** panel-<role>
   **This is round 1** of the review.
   ```

**Dispatch all reviewers in ONE assistant message** (parallel `Task` calls).

### Step 9: Optional convergence round

If `mode_b_convergence: true` AND `--no-convergence` NOT passed:

Dispatch each reviewer again with `<<<OTHER_ROLES_ROUND_1>>>` populated with
all other reviewers' round-1 blocks. Suffix: "This is round 2. Any of your
issues already covered by another reviewer — mark 'covered by panel-<name>'. Any
issues you now see you missed — add them." Keep the shared prefix identical.

### Step 10: Filter by focus

If `focus` ≠ `all`, filter issues to the focus area:
- `quality` → writing clarity, structure, consistency
- `completeness` → missing sections, gaps vs stated objective
- `risk` → risk to delivery, client relationship, quality
- `compliance` → red-line violations + regulatory concerns

Red-line violations always appear regardless of focus.

### Step 11: Synthesize + emit

```markdown
# 📋 Panel Review — <document name>

**Focus:** <focus>
**Reviewers:**
- panel-<r1>
- panel-<r2>

---

## ⚠️ Red Line Violations (auto-flagged pre-pass + reviewer additions)

- [critical] <text> — Source: panel-<role> — Location: <where>
- [major] ...
- [minor] ...

(Omit if none found.)

## 📐 Operating-Principle Conflicts

- [principle-conflict] "<principle quoted>" — Source: panel-<role> — Location: <where> — Severity: <major|minor>

(Omit if none found.)

## Reviewer-by-reviewer

<per-reviewer blocks from Step 8/9>

## Aggregate recommendations

<top 3–5 concrete changes, severity-ordered, deduplicated across reviewers>

## 📎 Suggested follow-ups

<Include bullets that apply:>
- If [critical] issues exist: `/panel-discuss "Address <specific issue>" --goal=problem-solving --continue=<thread_id>`
- If redraft needed: `/panel-draft "<section>" --roles=<best-owning-role>`
- If minor-only: show top 3 inline fixes
```

Observability footer + Recon Diagnostics required (same as panel-discuss).

### Step 12: Log

Write to resolved output path. Support `--continue=<thread_id>` for iterative
review rounds on the same document.

## Self-check before emitting

- [ ] Document was NOT truncated
- [ ] Red-line pre-pass ran against every reviewer's Red Lines
- [ ] Operating-Principle soft check ran against every reviewer's Operating Principles
- [ ] Each reviewer produced Strengths + Issues + Recommendations + `_Consulted:`
- [ ] Per-reviewer issues ≤8 (overflow rolled into Additional observations)
- [ ] Aggregate recommendations are concrete and severity-ordered
- [ ] Grounding check: if bundle non-empty, >50% of reviewers cite ≥1 `[E-id]`
- [ ] If any [critical] issues: Suggested follow-ups includes problem-solving discussion
- [ ] Observability footer + Recon Diagnostics present
- [ ] Log written to resolved path

If any item fails, fix before emitting.
