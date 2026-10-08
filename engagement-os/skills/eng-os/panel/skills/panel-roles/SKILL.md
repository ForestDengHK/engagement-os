---
name: panel-roles
description: Manage the panel agent roster. Subcommands - `list` (show all available agents with one-liner descriptions), `show <role>` (print full agent file), `recommend <topic>` (suggest 3-7 agents relevant to a topic), `map` (render the stakeholder map from project-context + roster), `threads` (list existing panel output threads). Use when the user asks "what roles are available", "which roles should I use for X", "show me panel-<role>", "stakeholder map", or "what panels have we run".
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
argument-hint: "list | show <role> | recommend \"<topic>\" | map | threads"
---

# /panel-roles — Manage the agent roster (v2)

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

## Subcommands

```
/panel-roles list
/panel-roles show <role>
/panel-roles recommend "<topic>"
/panel-roles map
/panel-roles threads
```

## Automation mode

All five subcommands are read-only, so automation semantics are simple:

- `list`, `show`, `threads` — always safe; print the requested output without
  any confirmation turn.
- `recommend` — always produces a ranked list; no approval needed.
- `map` — reads `.claude/project-context.md`; if it is missing, emit a single
  line pointing to `/panel-init` and stop rather than starting an interview.
- If a required argument is missing (`show <role>`, `recommend "<topic>"`),
  emit a `Missing inputs:` checklist and stop.

## Resolution order

Before executing any subcommand, run the root resolver script and use the
returned absolute paths.

Every subcommand looks in both locations and merges, with project overrides
taking precedence:

1. `<project_root>/.claude/agents/panel-*.md` (project overrides — win on
   name collision)
2. `<plugin_root>/agents/panel-*.md` (plugin defaults)

The merged roster is the "effective roster".

## Subcommand: list

Print the effective roster, grouped by category (inferred from the role's
description):

```
## Delivery / engagement (N)
- panel-engagement-partner — <1-line desc>
- panel-solution-architect — <1-line desc>
- ...

## Data & AI (N)
- panel-data-architect — <1-line desc>
- ...

## Client-side (N)
- panel-client-sponsor — <1-line desc>
- ...

## External (N)
- panel-regulator-perspective — <1-line desc>

Total: N agents (M from plugin, K project overrides)
```

The 1-line desc is the first sentence of the agent's `description:` frontmatter.

### `--verbose`

Include model + color + file path per agent.

## Subcommand: show

`/panel-roles show <role>` — print the full agent file (cat the .md).
Accept role name with or without `panel-` prefix; resolve to canonical name.

If role not found: suggest closest match via string distance.

## Subcommand: recommend

`/panel-roles recommend "<topic>"` — suggest 3–7 agents relevant to the topic.

Procedure:
1. Extract keywords from the topic.
2. For each agent in the effective roster, score by keyword overlap with the
   agent's `description` + `Responsibilities` + `Typical Questions` + `Known Positions`.
3. Return top 3–7 agents sorted by score, each with a 1-sentence rationale for
   why it matches the topic.

```
## Recommended for "<topic>"

- panel-<role-1> — <1-sentence why: which agent section matched>
- panel-<role-2> — <1-sentence why>
- ...

Not recommended but adjacent:
- panel-<role-N> — <why it almost made the cut>

Missing? Try `/panel-new-role "<description>"` to create one.
```

## Subcommand: map

`/panel-roles map` — render the stakeholder map from
`.claude/project-context.md` Stakeholder Map section, annotated with agent
resolution.

```
# Stakeholder Map (resolved)

## Our Side
- Forest Deng — Engagement Partner → panel-engagement-partner ✓ (plugin)
- Mike Henderson — Data Platform Lead → panel-data-architect ✓ (project override)
- ...

## Client Side
- Eddie Dillon — Primary reporting contact → panel-client-project-manager ✓ (plugin)
- ... → ⚠ panel-some-role (agent MISSING — create via /panel-new-role)

## External
- CRU regulator perspective → panel-regulator-perspective ✓ (plugin)

## Diagnostics
- N stakeholders mapped to M unique panel-<role> agents
- K agents missing — listed above
```

## Subcommand: threads

`/panel-roles threads` — list existing panel output threads.

Scan `<output_base>/{discussions,drafts,reviews,debriefs,refresh}/*.md`. For
each thread file, extract:
- thread_id (filename without .md)
- skill (from the directory name)
- topic (from file header)
- last updated (file mtime)
- rounds (count of `## Round ` markers in file)

Print in a table sorted by mtime descending.

```
## Panel Threads

| Skill | Thread | Topic | Rounds | Last updated |
|-------|--------|-------|--------|--------------|
| discuss | cloud-migration-2026-04-20 | Cloud-native DWH decision | 2 | 2026-04-20 |
| review | draft-methodology-2026-04-18 | Methodology section review | 1 | 2026-04-18 |
| ...

Total: N threads across <S> skills.

Tip: continue an existing thread with `--continue=<thread_id>`
```

### Subcommand: threads `--filter=<pattern>`

Filter threads by substring match in thread_id or topic.

## Self-check

- [ ] Effective roster computed from both plugin and project paths
- [ ] Duplicate names resolved project-wins
- [ ] Subcommand output matches documented format
- [ ] `show` handles missing role gracefully
- [ ] `recommend` ranks by content overlap, not alphabetically
- [ ] `map` handles missing agents with explicit ⚠ marker
- [ ] `threads` reads from configured output_base, not hardcoded path

If any item fails, fix before finishing.
