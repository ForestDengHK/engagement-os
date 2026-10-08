---
name: panel-new-role
description: Create a new project-local panel agent interactively. Walks user through Role Brief, Responsibilities, Reference Frameworks, Operating Principles, Priorities, Communication Style, Typical Questions, Known Positions, Red Lines, Works Most Closely With. Auto-appends the standard Contribution Protocol footer. Writes to `.claude/agents/panel-<slug>.md`. Use when the user says "add a new role", "I need a <X> perspective", "create panel-<name>", or when an existing discussion surfaces a missing role that isn't in the 33 plugin defaults.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
argument-hint: "\"<role description>\" [--clone-from=<role>] [--dry-run]"
---

# /panel-new-role — Interactive agent creation (v2)

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

- An existing panel discussion flagged a missing role in "Recommended Next Round"
- User explicitly wants a new project-specific role (e.g., "CRU regulatory liaison" specialized beyond the generic `panel-regulator-perspective`)
- Cloning a plugin role to customize for this project (pre-fill from plugin, edit, save to project overrides)

## Inputs

| Input | Required | Default |
|-------|----------|---------|
| description | yes | Ask — one-paragraph description of the role |
| slug | no | Auto-generate from description; user confirms |
| clone_from | no | `/panel-new-role --clone-from=<existing-role>` pre-fills from existing agent |

Flags:
- `--clone-from=<role>` — pre-populate persona sections from existing plugin or project agent
- `--dry-run` — show generated file without writing

## Automation mode

- If the current user turn provides the 11 creation inputs as a labeled block
  (title / brief / responsibilities / frameworks / principles / priorities /
  communication style / typical questions / known positions / red lines /
  works most closely with), skip the per-section walk and assemble the file
  in one pass. Ensure the frontmatter `description` is composed from
  brief + frameworks + red lines + a concrete trigger clause to exceed 100
  chars before writing.
- If `--dry-run` is present in an otherwise automated run, print the full
  generated agent file and exit without writing.
- If required inputs are missing in a non-interactive run, emit a
  `Missing inputs:` checklist naming the missing persona sections and stop.
- In automation mode:
  - default `model` to `sonnet` and `color` to `blue` unless explicitly
    requested
  - default Stakeholder Map registration to `no` unless explicitly requested
  - always run the two validation tests at Step 7 and fail loudly on schema
    violations rather than asking "do you want me to fix this"

## Step-by-step

### Step 1: Collect description

If not provided, ask: "One paragraph: who is this role, what do they own, what's distinct about their perspective?"

### Step 2: Check for near-duplicates

Scan the effective roster (`<project_root>/.claude/agents/` +
`<plugin_root>/agents/`). For each existing role, compute semantic similarity
to the new description. If any existing role scores > 0.8 (overlap in
responsibilities + frameworks + priorities):

```
⚠ Near-duplicate detected:
- panel-<existing> looks ~85% overlapping with your description.
  Reason: <which sections match>

Options:
- A. Use existing panel-<existing>
- B. Override panel-<existing> with a project-local customization (I'll pre-fill from plugin, you edit)
- C. Proceed anyway and create a new role (choose this if the distinction is meaningful)
```

### Step 3: Generate slug

Propose a slug (kebab-case, lowercase, no `panel-` prefix). Confirm with user.

Final name: `panel-<slug>`.

### Step 4: Walk persona sections

Walk through the 11 creation inputs one at a time:

1. **Title** (for `# Panel Role:` heading)
2. **Role Brief** (1–2 sentences, identity in the engagement)
3. **Responsibilities** (5–8 bullets — day-to-day activities)
4. **Reference Frameworks** (3–6 named books / standards / practitioners with 1-line context each, and URLs where canonical)
5. **Operating Principles** (3–5 decision rules — how this role decides, not what they do)
6. **Priorities** (4–6 things they care about, ranked)
7. **Communication Style** (3–5 lines — how they speak, what they challenge)
8. **Typical Questions** (5–8 questions they'd ask unprompted)
9. **Known Positions** (0–3 specific stances they hold, optional)
10. **Red Lines** (3–5 things they refuse to accept)
11. **Works Most Closely With** (3–5 other `panel-<role>` adjacencies with 1-line rationale)

If `--clone-from=<existing-role>` was used, pre-fill each section with the
cloned content and ask "Keep, edit, or replace?" for each.

### Step 5: Generate frontmatter

- `name: panel-<slug>`
- `description:` — compose from Role Brief + Frameworks names + Red Lines + Priorities, matching the template used by the 33 plugin agents (should exceed 100 chars)
- `disallowedTools: Bash, Edit, Write, NotebookEdit, Agent, Task`
- `model:` — ask user: `sonnet` (default) or `opus` (for synthesis-heavy roles)
- `maxTurns: 8` — standard bounded-runtime default for panel roles
- `color:` — ask user: pick from red/blue/green/yellow/purple/orange/pink/cyan

### Step 6: Append Contribution Protocol

Copy the standard Contribution Protocol footer verbatim (same as all plugin
agents — Dig Rule, Grounding Rule, Output Format, Self-check).

### Step 7: Write or dry-run

If `--dry-run`: print the full generated file, exit.

Otherwise:
- Ensure `<project_root>/.claude/agents/` exists (`mkdir -p`)
- Write to `<project_root>/.claude/agents/panel-<slug>.md`
- Run `<plugin_root>/tests/test-agents-schema.sh <project_root>/.claude/agents/panel-<slug>.md`
  and `<plugin_root>/tests/test-agent-name-collision.sh <plugin_root>/agents <project_root>/.claude/agents`
  to validate; if either fails, show the user the violation and offer to fix

### Step 8: Register in project-context (optional)

Ask: "Add this role to the Stakeholder Map in `.claude/project-context.md`? (Our side / Client side / External)"

If yes, append to the appropriate subsection.

### Step 9: Emit summary

```
✅ Created panel-<slug> at .claude/agents/panel-<slug>.md

Model: <model> | Color: <color>
Frameworks: <list>
Red Lines: <count>

Validation: PASS (agents schema test)

Next step: use this role in a panel —
  /panel-discuss "<topic>" --roles=panel-<slug>,<other roles>
```

## Self-check before finishing

- [ ] Name is lowercase-kebab with `panel-` prefix
- [ ] Description ≥100 chars with concrete trigger phrases
- [ ] All 9 required body sections present
- [ ] Contribution Protocol footer present (Dig Rule + Grounding Rule + Output Format + Self-check)
- [ ] `tests/test-agents-schema.sh` passes
- [ ] `tests/test-agent-name-collision.sh` passes (no duplicate)
- [ ] If `--clone-from` was used: cloned content was edited, not left verbatim
- [ ] If Stakeholder Map update was offered, user choice was recorded
