---
name: panel-edit-role
description: Edit an existing panel agent's persona fields (Responsibilities, Reference Frameworks, Operating Principles, Priorities, Communication Style, Typical Questions, Known Positions, Red Lines, Works Most Closely With) or frontmatter (description, model, maxTurns, color, disallowedTools). Auto-copies a plugin agent to `.claude/agents/` on first edit so plugin defaults stay intact. Use when the user says "tweak panel-<role>", "update <role>'s red lines", "change <role>'s model to opus", or wants to refine an existing agent's behavior in this project.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
argument-hint: "<role> [field] [--diff]"
---

# /panel-edit-role — Targeted edits to an existing agent (v2)

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

- Refine a plugin role for project-specific tailoring (e.g., `panel-client-sponsor` should know this client's actual reporting cadence)
- Update a role after learning from dogfood (e.g., add a Red Line that's been violated twice)
- Upgrade or downgrade a role's model
- Adjust description for better trigger matching

## Inputs

| Input | Required | Default |
|-------|----------|---------|
| role | yes | Ask — which `panel-<role>` to edit |
| field | no | Ask — which section to edit (see list below) |

Flags: `--diff` (show diff without saving), `--no-log`.

## Automation mode

- If the current user turn specifies both `role` and `field` plus the edit
  content (replace / append / remove payload), proceed directly: read the
  role, apply the edit in memory, run schema validation, show the diff, and
  save.
- If the edit would change `disallowedTools`, `model`, or `maxTurns`, always
  show the diff and require an explicit acknowledgement line in the user's
  turn ("confirm disallowedTools change"); these three fields carry runtime
  risk and should not be silently mutated.
- If required inputs (role, or field when the user has named edit content)
  are missing in a non-interactive run, emit a `Missing inputs:` checklist
  and stop.
- `--diff` always wins: if present, validate and emit the diff but never
  write the file.

### Editable fields

**Frontmatter:**
- `description`
- `model` (sonnet | opus | haiku)
- `maxTurns` (recommended default `8`)
- `color` (red | blue | green | yellow | purple | orange | pink | cyan)
- `disallowedTools` (standard default: `Bash, Edit, Write, NotebookEdit, Agent, Task`)

**Body sections:**
- Role Brief
- Responsibilities
- Reference Frameworks
- Operating Principles
- Priorities
- Communication Style
- Typical Questions
- Known Positions
- Red Lines
- Works Most Closely With

`name` is NOT editable (changes filename; use `/panel-new-role --clone-from=<old>` + delete if renaming).

Contribution Protocol is NOT editable (it's the standard template; changing
it breaks orchestrator assumptions).

## Step-by-step

### Step 1: Resolve the role

Check project-local first: `<project_root>/.claude/agents/panel-<role>.md`.
If not found: check plugin: `<plugin_root>/agents/panel-<role>.md`.

If role exists only in plugin: announce "this is a plugin-default role; I'll
copy it to `<project_root>/.claude/agents/panel-<role>.md` so your edits don't
affect the plugin. Continue?"

If user says yes: `cp` the plugin file to project path. Subsequent edits apply
to the project copy, which overrides plugin per Claude Code resolution.

If role doesn't exist at all: suggest `/panel-new-role` instead.

### Step 2: Pick field to edit

If not specified, show a menu:

```
Edit panel-<role>. Pick a field:

Frontmatter:
  1. description
  2. model (currently: sonnet)
  3. maxTurns (currently: 8)
  4. color (currently: blue)
  5. disallowedTools (currently: Bash, Edit, Write, NotebookEdit, Agent, Task)

Body sections:
  6. Role Brief (42 words)
  7. Responsibilities (7 bullets)
  8. Reference Frameworks (5 items)
  9. Operating Principles (5 items)
 10. Priorities (5 items)
 11. Communication Style (3 items)
 12. Typical Questions (6 items)
 13. Known Positions (2 items)
 14. Red Lines (4 items)
 15. Works Most Closely With (5 items)

Enter number(s) or section name:
```

User can pick multiple.

### Step 3: Edit flow

For each selected field:

1. Show current content.
2. Prompt for the edit mode:
   - `replace` — replace the entire section
   - `append` — add items/text to the end
   - `remove` — remove specific bullets/lines
   - `rewrite` — walk bullet-by-bullet
3. Apply the edit in memory.

For `description`: after edit, verify length ≥100 chars.
For `model`: validate value.
For `maxTurns`: validate integer ≥1 and keep it bounded (recommended 4–12).
For `color`: validate value.
For `disallowedTools`: keep `Bash, Edit, Write, NotebookEdit, Agent, Task`
blocked unless the user explicitly understands they are changing the standard
runtime guardrails.

### Step 4: Show diff

Print a unified diff of the changes (before / after).

If `--diff` flag: stop here, do not save.

Ask: "Apply changes?" (yes / edit-again / cancel)

### Step 5: Validate + save

Run in-memory validation against the agent schema (same checks as
`<plugin_root>/tests/test-agents-schema.sh`). If violations: show them, loop
back to edit.

Save to `<project_root>/.claude/agents/panel-<role>.md`.

### Step 6: Log + emit

```
✅ Updated panel-<role>.md

Fields changed:
- <field 1>: <brief summary>
- <field 2>: <brief summary>

Location: .claude/agents/panel-<role>.md
Validation: PASS

If this role was recently used in a panel and behavior was surprising, re-run
that panel with --continue=<thread_id> to see the edits take effect.
```

Append to `<output_base>/refresh/role-edit-<role>-<YYYY-MM-DD>.md` unless
`--no-log`: the change log (what fields changed, diff, reason).

## Self-check

- [ ] Project path used (plugin file never modified in-place)
- [ ] After edit, `tests/test-agents-schema.sh` on the file passes
- [ ] After edit, `tests/test-agent-name-collision.sh` passes
- [ ] description ≥100 chars
- [ ] MCP inheritance preserved unless the user explicitly changed the standard guardrails
- [ ] Diff was shown before save (unless user pre-approved)
- [ ] Log written unless `--no-log`

If any item fails, fix before saving.
