#!/usr/bin/env bash
# framework-scripts/resolve-roots.sh — authoritative project/plugin root resolver
#
# Resolves two paths:
#   project_root — nearest ancestor of $PWD that contains `.claude/` or `.git/`
#                  (falls back to $PWD if neither is found). This handles the
#                  "user invoked the skill from a subdirectory" case, which
#                  would otherwise silently scope Recon to a subtree and miss
#                  `.claude/project-context.md`.
#   plugin_root  — first candidate that is a panel-framework plugin root
#                  (`.claude-plugin/plugin.json` naming "panel-framework"):
#                    1. CLAUDE_PLUGIN_ROOT env var
#                    2. the parent directory of this script (plugin checkout)
#                    3. the newest installed version under
#                       ${CLAUDE_CONFIG_DIR:-~/.claude}/plugins/cache/panel-framework/panel-framework/
#                  Candidate 3 is what makes a project-local copy of this
#                  script (`<project>/.claude/framework-scripts/`) work: there
#                  the parent directory is `<project>/.claude`, which is not a
#                  plugin root, and CLAUDE_PLUGIN_ROOT is unset for project skills.
#
# If project_root would equal plugin_root (i.e. the user is developing the
# plugin itself and $PWD is inside the plugin checkout), the walk-up still
# stops at the plugin checkout — which is what a plugin maintainer wants for
# dogfooding. In that case the invariant
# `<project_root>/.claude` ≠ `<plugin_root>/.claude` may not hold; downstream
# skills that forbid reading `<plugin_root>/.claude/` should still error
# loudly rather than silently use it.
#
# Usage:
#   bash "/abs/path/to/panel-framework/framework-scripts/resolve-roots.sh"
#
# Output (stdout, exactly two lines):
#   project_root=/abs/path
#   plugin_root=/abs/path
#
# Exits:
#   0 — resolved successfully
#   2 — no candidate is a valid panel-framework plugin root

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Plugin root -----------------------------------------------------------

is_plugin_root() {
  [[ -n "$1" && -f "$1/.claude-plugin/plugin.json" ]] &&
    grep -q '"name"[[:space:]]*:[[:space:]]*"panel-framework"' "$1/.claude-plugin/plugin.json"
}

PLUGIN_CACHE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/cache/panel-framework/panel-framework"
NEWEST_INSTALLED="$(ls -d "$PLUGIN_CACHE"/[0-9]* 2>/dev/null | sort -V | tail -1 || true)"

PLUGIN_ROOT=""
for candidate in "${CLAUDE_PLUGIN_ROOT:-}" "$SCRIPT_DIR/.." "$NEWEST_INSTALLED"; do
  if is_plugin_root "$candidate"; then
    PLUGIN_ROOT="$(cd "$candidate" && pwd -P)"
    break
  fi
done

if [[ -z "$PLUGIN_ROOT" ]]; then
  echo "Invalid plugin root: none of CLAUDE_PLUGIN_ROOT='${CLAUDE_PLUGIN_ROOT:-}', $SCRIPT_DIR/.., $PLUGIN_CACHE/<version> contains a panel-framework .claude-plugin/plugin.json" >&2
  exit 2
fi

# --- Project root (walk up from pwd) --------------------------------------

START="$(pwd -P)"
PROJECT_ROOT="$START"
cursor="$START"
while :; do
  if [[ -d "$cursor/.claude" || -d "$cursor/.git" ]]; then
    PROJECT_ROOT="$cursor"
    break
  fi
  parent="$(dirname "$cursor")"
  if [[ "$parent" == "$cursor" ]]; then
    # Reached filesystem root without finding .claude/ or .git/ —
    # fall back to $PWD. Downstream skills will surface the missing
    # `.claude/project-context.md` and direct the user to /panel-init.
    break
  fi
  cursor="$parent"
done

printf 'project_root=%s\n' "$PROJECT_ROOT"
printf 'plugin_root=%s\n' "$PLUGIN_ROOT"
