---
name: panel-refresh
description: Refresh project context and agent roster after significant engagement changes. Updates `.claude/project-context.md` interactively (not overwriting user edits blindly), validates that referenced agents exist, optionally pulls fresh info from the repo (recent decisions, new stakeholders, phase transitions). Use when the user says "refresh panel", "update project context", "stakeholders have changed", "new phase started", or when project-context.md is visibly stale compared to the repo state.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
argument-hint: "[--focus=<context|roles|references|all>] [--dry-run]"
---

# /panel-refresh — Update project context and agent roster (v2)

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

- After a phase transition (e.g., mobilisation → discovery)
- After a material scope change, stakeholder change, or compliance posture change
- When project-context.md is visibly out of sync with the repo's state
- Periodically (e.g., monthly on long engagements)

## Inputs

| Input | Required | Default |
|-------|----------|---------|
| reason | no | Ask — "why are we refreshing?" (phase / stakeholder / scope / periodic / other) |
| focus | no | `all` — one of `context | roles | references | all` |

Flags: `--dry-run` (show changes without writing), `--no-log`.

## Automation mode

- If a non-interactive run, default `--dry-run` behavior: surface the proposed
  unified diffs and stop. Do not silently mutate `.claude/project-context.md`
  without an explicit confirmation turn or an explicit `--apply` in a future
  iteration of this skill.
- If the current user turn explicitly says "apply all proposed updates" or
  provides a labeled list of accepted changes, skip per-section confirmation
  and write them in one batch. Still show the final diff in the emitted log.
- If required inputs (`reason` when not defaulted) are missing in a
  non-interactive run, emit a `Missing inputs:` checklist and stop.

## Step-by-step

### Step 1: Load current state

Run the root resolver script first and cache the returned absolute
`project_root` and `plugin_root`. Read
`<project_root>/.claude/project-context.md` and
`<project_root>/.claude/panel-config.yaml`. If either is missing, direct user
to `/panel-init`.

### Step 2: Scan repo for deltas

Use Recon-style Glob + Grep to surface:
- New / modified artifacts since the `Last updated` timestamp in project-context.md (if present) — files under `01_rfp/`, `02_implementation/`, `docs/`, etc.
- New role names mentioned in recent commits or documents (new stakeholders)
- Decisions made since last refresh (mentioned in meeting notes, draft artifacts, review threads)

Show the user a delta summary:

```
🔄 Repo deltas since last refresh (<date>):
- 12 new files in 02_implementation/1_discovery/
- 3 new client-side names mentioned: <names>
- 2 new decisions in panel/discussions/ threads
- 1 new risk surfaced in panel/reviews/
```

### Step 3: Propose context updates

For each delta that suggests a project-context.md update, propose the edit.
Present as unified diffs. Ask user to accept, reject, or modify each.

Categories to walk through:
- **Timeline** — new phase dates, new milestones
- **Scope / Out of scope** — changes agreed with client
- **Key technology** — newly-discovered systems, EOL dates, architectural decisions
- **Stakeholder map** — new client-side contacts, new Deloitte SMEs, external perspectives
- **Compliance & constraints** — new regulations, liability changes, insurance updates
- **Known pain points** — new ones surfaced in discovery; old ones resolved
- **Key decisions made** — append new decisions with date + rationale

Do not overwrite user edits silently. If a section appears to have been
hand-edited since last refresh, flag and ask before touching.

### Step 4: Validate agent references

For each `panel-<role>` mentioned in the updated project-context.md Stakeholder
Map:
- Check if agent exists (plugin `agents/panel-<role>.md` OR project `.claude/agents/panel-<role>.md`)
- If missing: offer to create via `/panel-new-role` or suggest closest existing role

### Step 5: (optional) Reference pack check

If `<project_root>/references/` exists:
- Check for stale notes (`last_updated` field older than ~90 days on time-sensitive ones like regulations)
- Suggest refresh actions: "compliance/eu-nis2-2022-2555.md is 120 days old; re-fetch authoritative source?"

### Step 6: Write updates

If `--dry-run`, print the diff and exit.

Otherwise:
- Update `.claude/project-context.md` with accepted changes
- Update the `Last updated:` timestamp at the top of the file
- Append a refresh entry to `<output_base>/refresh/<YYYY-MM-DD-refresh>.md`
  (thread-id format: `refresh-YYYY-MM-DD` with suffix on collision) listing
  what was changed and why

### Step 7: Emit summary

```
✅ Panel refresh complete (<reason>).

Context updates:
- <section>: <brief change>

Agent roster:
- <panel-role>: OK (plugin) | OK (project override) | MISSING (action: ...)

Reference pack:
- <note>: current | stale (<days old>) | missing

Refresh log written to: <path>
```

## Self-check before finishing

- [ ] `.claude/project-context.md` `Last updated` timestamp is today
- [ ] No silent overwrite — each accepted change was explicit
- [ ] All referenced `panel-<role>` agents exist or user was told how to create them
- [ ] Refresh log written (unless `--no-log` or `--dry-run`)
- [ ] User saw a diff before changes were applied

If any item fails, fix before finishing.
