---
name: panel-init
description: Initialize the panel framework in a new project. Creates `.claude/project-context.md`, `.claude/panel-config.yaml`, and optional project-local agent overrides. Scaffolds `.mcp.json` to register context7 for roles that need authoritative external documentation. Use when starting a new project, onboarding an existing project to the panel framework, or resetting panel state.
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash"]
argument-hint: "[project summary or field list]"
---

# /panel-init — Onboarding (v2)

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

- Starting a new engagement and want to use panel-framework
- Adopting an existing engagement to panel-framework
- Resetting panel state after deletion of `.claude/`

## Automation mode

- If the current user turn already provides all 10 project-context fields, parse
  them and write files directly. Do not re-ask the same interview questions.
- A single labeled list counts as complete input if it materially covers these
  10 fields. Treat close label matches as equivalent, for example:
  `Project name and identifier` → Project Name, `Recent key decisions` → Key
  Decisions Made, `Compliance and constraints` → Compliance & Constraints.
- If required fields are missing in a non-interactive run, emit a `Missing
  fields:` checklist and stop instead of starting the interview.
- In automation mode:
  - default project-local role overrides to `no` unless explicitly requested
  - keep config defaults unless explicit overrides are provided
  - default context7 setup to `no` unless explicitly requested
  - seed template-only sections that were not part of the 10-field intake:
    - `Reference Pack`: root `references/`, key local references `To be confirmed`, gaps `To be confirmed`
    - `Inherited Context`: `None stated at initialization`
  - execute the file-writing steps immediately once the field list is complete;
    do not pause to ask optional follow-up questions

## Step-by-step

### Step 1: Check state

Run the root resolver script first and cache the returned absolute
`project_root` and `plugin_root`.

Look for these files:
- `<project_root>/.claude/project-context.md`
- `<project_root>/.claude/panel-config.yaml`

If both exist: ask the user whether to reinitialize (yes → delete and proceed;
no → exit).

### Step 2: Project-context interview

Walk the user through building `<project_root>/.claude/project-context.md`
using the template at `<plugin_root>/templates/project-context.template.md`.
If all 10 fields are already present in the current user turn, skip the
interview and populate the template directly. In that direct path, read the
template, create `<project_root>/.claude/` if missing, fill every section, and
write the file before moving on.

Ask, one field at a time:
1. Project name and identifier
2. Client (legal entity, sector, regulatory posture)
3. Timeline (tender date, contract status, term, phases)
4. Scope and Out of Scope
5. Key technology
6. Known pain points
7. Stakeholders (our side / client side / external) — ask which roles they expect to need; map each to a `panel-<role>` agent
8. Compliance and constraints
9. Recent key decisions
10. Project type

If required fields are missing and the run is non-interactive, emit the
missing-fields checklist and stop.
Otherwise, write responses into the template structure and save to
`.claude/project-context.md`.

When filling the template:
- `Reference Pack` may be initialized with placeholders if the user did not
  provide reference-pack details yet.
- `Inherited Context` may be initialized to `None stated at initialization` if
  no prior-project carry-over was provided.
- `Project Type` is a prose label in the context document, not a config key.

### Step 3: Propose agent usage

Based on the stakeholder map and project type, suggest which of the 33 plugin
agents are most likely to participate. Three categories:

- **Always-on** (recommended for every project): `panel-engagement-partner`, `panel-project-manager`, `panel-quality-reviewer`
- **Project-type-specific** — e.g., data engagements: `panel-data-architect`, `panel-data-engineer`, `panel-data-scientist`, `panel-responsible-ai-lead` (if AI); delivery engagements: `panel-solution-architect`, `panel-technical-lead`, `panel-security-lead`
- **Client-side**: `panel-client-sponsor`, `panel-client-project-manager`, plus project-specific (`panel-data-owner`, `panel-enterprise-architect-client`, `panel-end-user-representative`)

Tell the user the plugin version is used automatically — no file needed in
`.claude/agents/` unless they want to customize a role for this project.

Ask: "Do you want to create project-local overrides for any of these roles
now?" If yes, prompt for each — copy the plugin agent file to
`.claude/agents/panel-<role>.md` and open for edit. If no, proceed.
In automation mode, default this answer to `no` unless the user explicitly
asked for overrides in the current turn.

### Step 4: Config

Copy `<plugin_root>/panel-config.default.yaml` to
`<project_root>/.claude/panel-config.yaml` **via an explicit `Bash` `cp`** so
that YAML comments are preserved byte-for-byte:

```bash
cp "$plugin_root/panel-config.default.yaml" "$project_root/.claude/panel-config.yaml"
```

Do NOT use `Read` + `Write` for this — that path reformats comments and may
drop structure. Only use `Read` + `Edit` if the user asks for a change.

Ask the user to review:
- `output_base` — default `panel/`
- `recon.confirm_with_user` — default `true` (interactive); set `false` for CI
- `mode_b_convergence` — default `true` (round 2 on)
- `panel_draft.review_focus` — default `all` (used only with `--with-review`)

If the user wants changes, edit in place.
In automation mode, write the shipped default config immediately and only apply
overrides that were explicitly provided in the current turn.

### Step 5: MCP setup for context7 (optional)

Ask: "Some panel roles that research external standards (security-lead,
responsible-ai-lead, regulator-perspective, legal-counsel, data-governance-lead)
benefit from context7 — Claude Code's MCP integration for authoritative library
and framework docs. Want to enable it?"

If yes:
- Check if `<project_root>/.mcp.json` exists.
  - If missing: create with:
    ```json
    {
      "mcpServers": {
        "context7": {
          "command": "npx",
          "args": ["-y", "@upstash/context7-mcp"]
        }
      }
    }
    ```
  - If exists but `context7` not registered: add the entry.
- Print reminder: "context7 will activate after you restart Claude Code."
In automation mode, skip this entire step unless the user explicitly asked to
enable context7.

### Step 6: `.gitignore` entries

Ensure `.gitignore` covers:

```
panel/_recon_cache/
.claude/settings.local.json
```

If `<project_root>/.gitignore` doesn't exist, create it.

In automation mode, do this without asking.

### Step 7: Summarize

```
✅ Panel framework v2 initialized for <project name>.

Files created:
- .claude/project-context.md
- .claude/panel-config.yaml
- .mcp.json (if context7 enabled)

Next step: run /panel-discuss "<your first topic>" to test the installation.
```

## Self-check before finishing

- [ ] `.claude/project-context.md` exists, non-empty, contains Project Name + Client + Timeline + Scope + Stakeholder Map + Project Type
- [ ] `.claude/panel-config.yaml` exists and matches v2 schema (tests/test-config-schema.sh would pass)
- [ ] If context7 opted in, `.mcp.json` exists with context7 entry
- [ ] `.gitignore` has the required entries
- [ ] User was told to run `/panel-discuss` next

If any item fails, fix before finishing.
