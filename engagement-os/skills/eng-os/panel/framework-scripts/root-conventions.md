<!-- framework-scripts/root-conventions.md
Shared root-resolution contract for every panel-* SKILL.md. Loaded by each
skill's "Root conventions" section. Edit here once; skills reference this
file by `<plugin_root>` path, so edits take effect across all 9 skills. -->

# Root conventions

Resolve both roots before any other work. Claude Code exposes
`${CLAUDE_SKILL_DIR}` for the active skill directory. Launch the shared root
resolver:

```bash
# The resolver takes plugin_root from the first of: (1) CLAUDE_PLUGIN_ROOT env var,
# (2) the parent directory of resolve-roots.sh itself, (3) the newest installed version
# under ${CLAUDE_CONFIG_DIR:-~/.claude}/plugins/cache/panel-framework/panel-framework/.
PF_CACHE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/panel-framework/panel-framework"
for d in "${CLAUDE_PLUGIN_ROOT:-}" "$(ls -d "$PF_CACHE"/[0-9]* 2>/dev/null | sort -V | tail -1)" "${CLAUDE_SKILL_DIR}/../.."; do
  [ -n "$d" ] && [ -f "$d/framework-scripts/resolve-roots.sh" ] &&
    { bash "$d/framework-scripts/resolve-roots.sh" || echo "resolver failed: $d" >&2; break; }
done
```

The resolver prints exactly two lines to stdout:

```
project_root=<abs path>
plugin_root=<abs path>
```

Treat that output as authoritative:

- **`project_root`** — the nearest ancestor of the current working directory
  that contains `.claude/` or `.git/`. Falls back to `$PWD` if neither is
  found (user gets a clear downstream error when
  `.claude/project-context.md` is missing). All project-local assets live
  here:
  - `<project_root>/.claude/project-context.md`
  - `<project_root>/.claude/panel-config.yaml`
  - `<project_root>/.claude/agents/panel-<role>.md` (project overrides)
  - `<project_root>/.claude/.mcp.json`
  - `<project_root>/panel/` (or whatever `output_base` is set to)
- **`plugin_root`** — the installed `panel-framework` plugin root.
  Resolver takes the first candidate that is a panel-framework plugin root
  (`.claude-plugin/plugin.json` naming "panel-framework"): (1) the
  `CLAUDE_PLUGIN_ROOT` env var, (2) the parent directory of the resolver
  script itself, (3) the newest installed version under
  `${CLAUDE_CONFIG_DIR:-~/.claude}/plugins/cache/panel-framework/panel-framework/`.
  Plugin-shipped assets
  live here — read-only from a skill's perspective:
  - `<plugin_root>/agents/panel-<role>.md` (plugin defaults)
  - `<plugin_root>/skills/.../prompts/*.md`
  - `<plugin_root>/skills/_shared/prompts/*.md`
  - `<plugin_root>/templates/*.md`
  - `<plugin_root>/framework-scripts/*.sh`
  - `<plugin_root>/panel-config.default.yaml`
  - `<plugin_root>/tests/*.sh`

Hard rules:

- Never read from or write to `<plugin_root>/.claude/` — it does not exist
  in the distributed plugin and any such path is a bug.
- Never use broad filesystem search (`find /`, speculative `Glob`) to guess
  `plugin_root`. Trust the resolver output.
- If the resolver exits non-zero, stop and surface the error instead of
  guessing. The resolver exits 2 when `plugin_root/.claude-plugin/plugin.json`
  is missing — that indicates a corrupted plugin install.
- Subagents dispatched via `Task` inherit no cwd guarantees. Every path a
  subagent receives in a dispatch prompt must be absolute. Build absolute
  paths by prefixing `<project_root>/` or `<plugin_root>/` to the relative
  form.
