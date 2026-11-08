---
name: panel-review
description: Multi-role review of a document. Each reviewer critiques from their priorities, red_lines, operating_principles, and reference_frameworks. Red_lines are auto-flagged against document content; Operating-Principle soft conflicts are surfaced too. `--focus=<area>` narrows the critique (quality / completeness / risk / compliance / all). Use when the user asks to "review", "critique", "challenge this draft", wants "X's take on my document", says "red-line check", "security review of <path>", "what would the architect flag here", or wants a draft "read as the buyer's evaluator" / scored against the published criteria.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task", "Agent", "Skill"]
argument-hint: "<file|directory|inline> [--roles=<role1,role2>] [--focus=<area>] [--as-evaluator]"
---

# /panel-review — Multi-role review (v2)

## Overview

v2 native-agents review. Same 5-phase pipeline as panel-discuss (Recon → Bundle
→ parallel dispatch → optional round 2 → synthesis), specialized for document
critique. Each reviewer is a native Claude Code subagent.

## Root conventions

Before any other work, run the shared root resolver to learn both
`project_root` and `plugin_root`. It is taken from the plugin first, then from
the project-local copy (`<project>/.claude/framework-scripts/`, planted by
`/panel-init` beside project-local skill copies):

```bash
PF_CACHE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/panel-framework/panel-framework"
for d in "${CLAUDE_PLUGIN_ROOT:-}" "$(ls -d "$PF_CACHE"/[0-9]* 2>/dev/null | sort -V | tail -1)" "${CLAUDE_SKILL_DIR}/../.."; do
  [ -n "$d" ] && [ -f "$d/framework-scripts/resolve-roots.sh" ] &&
    { bash "$d/framework-scripts/resolve-roots.sh" || echo "resolver failed: $d" >&2; break; }
done
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
| document | yes | Ask — a file path, inline content, or **a directory of markdown files** |
| roles | no | Propose 3–5 based on document content + project context |
| focus | no | `all` — one of `quality | completeness | risk | compliance | all` |
| continue (thread_id) | no | New thread |

Flags: `--no-recon`, `--recon-only`, `--force-dig`, `--no-convergence`, `--max-bundle-tokens=<N>`, `--keywords=<list>`, `--context=<paths>`, `--no-log`, `--as-evaluator` (see Evaluator mode).

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

- If inline, use the inline content.
- If a file, read it fully. **Do NOT truncate.**
- If a directory, build the **file index** — every `*.md` in it, sorted by name,
  one row each: `name · title (first H1, else the filename) · size (KB)`.

Then cut the **reading assignment** (a single file counts as a one-file set):

- **Set ≤ 60 KB** → every reviewer gets the full set, one pass.
- **Set > 60 KB** → pack the files in index order into chunks of ≤ 60 KB (a
  single file > 60 KB is split at its H2 headings). Each reviewer gets **pass 1**
  = one chunk and **pass 2** = one more chunk (Step 8). Give each reviewer
  first the chunk closest to its priorities, and spread the chunks so every
  chunk has at least one reviewer in pass 1.
- Every file a reviewer did not get in either pass is listed by name under
  its `_Consulted:` line as unread. Nothing is silently dropped.

Chunk contents are passed **inline** in the dispatch prompt, each file headed
`<!-- file: <name> -->`, so a reviewer spends its turns reviewing, not reading.

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

Resolve output path:

```bash
bash <plugin_root>/framework-scripts/resolve-output-path.sh \
  --project-root <project_root> \
  --skill review \
  --thread-id <thread_id>
```

For a directory, the document-basename-slug is the directory name.

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
   - `<<<FILE_INDEX>>>` — the Step 2 file index (or "(single document)")
   - `<<<READING_ASSIGNMENT>>>` — this reviewer's pass-1 files, its pass-2
     files, and the files it will not receive
   - `<<<DOCUMENT_CONTENT>>>` — the pass-1 content: full document text, or
     this reviewer's chunk
   - `<<<EVIDENCE_BUNDLE>>>` — bundle from Step 6 (or "(Recon skipped)")
   - `<<<REDLINE_VIOLATIONS>>>` — this reviewer's red-line pre-pass findings
   - `<<<PRINCIPLE_CONFLICTS>>>` — this reviewer's operating-principle findings
   - `<<<OTHER_ROLES>>>` — comma-separated other reviewers
2. `<plugin_root>/skills/panel-review/prompts/review-output-format.md` — the
   "Review Output Format" section (in evaluator mode, the "Evaluator Output
   Format" section instead)
3. Role-specific suffix:
   ```
   **Your role:** panel-<role>
   **This is round 1** of the review.
   ```

**Dispatch all reviewers in ONE assistant message** (parallel `Task` calls,
same form as `/panel-discuss` Step 6).

**Turn budget.** `Task` takes no per-call turn limit, so the limit is the
agent's `maxTurns` — 20 on every plugin agent (raised from 8 for this skill;
see the agent files). Inline content keeps a review to a few turns. A
project-local override in `<project_root>/.claude/agents/` keeps its own
`maxTurns`; if it is below 20 for a multi-file review, say so in the
Observability footer.

**Pass 2** (set > 60 KB only). When a reviewer's pass-1 block arrives, resume
that same agent with its pass-2 chunk inline and: "Pass 2: here are more files.
Return your complete block again, updated with these files; list unread files
under `_Consulted:`." If the harness cannot resume an agent, dispatch it afresh
with its pass-1 block pasted above the pass-2 chunk. The pass-2 block replaces
the pass-1 block.

**Resume rule.** A reviewer that returns no block (no `**Reviewer:**` /
`**Evaluator:**` line) is resumed **once** with: "Write your block now from
what you have read; list unread files under `_Consulted:`." If it still returns
nothing, continue without it and name it in the synthesis as failed.

### Step 9: Optional convergence round

If `mode_b_convergence: true` AND `--no-convergence` NOT passed AND not
`--as-evaluator`:

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

Observability footer + Recon Diagnostics required (same as panel-discuss). For a
directory, the footer carries the file index with, per file, which reviewers
read it.

In evaluator mode, `## Reviewer-by-reviewer` holds the evaluator block(s) and
`## Aggregate recommendations` is the five ranked moves (merged and re-ranked if
more than one evaluator ran).

### Step 12: Log

Write to resolved output path. Support `--continue=<thread_id>` for iterative
review rounds on the same document.

### Step 12b: Append to the score-gap register (evaluator mode only)

Locate the register: `<project_root>/01_pursuit/*/2_analysis/score_gap_register.md`
(first match).

- **Present:** take the evaluator's `gap-register` block. Append the header row
  under the first table and the gap rows under the second. Fill `Round` (one
  more than the highest existing Round) and assign each gap row a `G-nn` ID
  continuing from the highest existing ID. Skip a gap row whose Criterion + Gap
  text already exists in the register with Status not `applied`. Print the
  register path and the number of rows added.
- **Absent:** print the block and tell the user the engagement-os template
  plants the register at `01_pursuit/<ENG-ID>/2_analysis/score_gap_register.md`.

## Evaluator mode (`--as-evaluator`)

Reads the draft the way the buyer will score it.

- **Roles:** only `panel-client-sponsor`, or the roles named with `--roles`.
- **Weights:** the published evaluation criteria and weights, from
  `<project_root>/.claude/project-context.md` or the RFP analysis (pass it with
  `--context=<path>`). Quote them into the dispatch. If neither publishes
  weights, write "weights not published — equal weights assumed" into the
  dispatch.
- **Prompt suffix** (after the role-specific suffix):
  ```
  Read as the buyer's evaluator. For each published criterion (weights from
  the project context or the RFP analysis), score 0–10 with one line of
  reasoning; give the weighted total; list the five changes that move the
  score most, each marked 'needs information only the bidder has' or
  'rewrite'; list what a top supplier would have included that is missing;
  list what would make you doubt them at the clarification meeting.
  ```
- **Output:** the "Evaluator Output Format" block in
  `prompts/review-output-format.md`.
- **Dispatch input:** paste the document text, or give a pre-extracted
  plain-text file path readable with the Read tool. Never give a shell command
  (panel agents have no shell).
- Steps 2–8 and 10–12 (including 12b) run as normal (reading assignment,
  red-line pre-pass, resume rule, log to the review thread); Step 9 is skipped.

## Self-check before emitting

- [ ] Every file in the index was read by ≥1 reviewer; every unread file is named in that reviewer's `_Consulted:`
- [ ] No reviewer missing: each one returned a block, was resumed once, or is named as failed
- [ ] Red-line pre-pass ran against every reviewer's Red Lines
- [ ] Operating-Principle soft check ran against every reviewer's Operating Principles
- [ ] Each reviewer produced Strengths + Issues + Recommendations + `_Consulted:` (evaluator mode: Scores + Weighted total + five tagged moves + Missing + Doubts + `_Consulted:`)
- [ ] Per-reviewer issues ≤8 (overflow rolled into Additional observations)
- [ ] Aggregate recommendations are concrete and severity-ordered
- [ ] Grounding check: if bundle non-empty, >50% of reviewers cite ≥1 `[E-id]`
- [ ] If any [critical] issues: Suggested follow-ups includes problem-solving discussion
- [ ] Observability footer + Recon Diagnostics present
- [ ] Log written to resolved path

If any item fails, fix before emitting.
