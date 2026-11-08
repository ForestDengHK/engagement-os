#!/usr/bin/env bash
# scaffold-reference-pack.sh — create the project-local reference pack skeleton
#
# Usage:
#   scaffold-reference-pack.sh --project-root /path/to/repo [--root references/] [--force]
#
# Creates:
#   <root>/README.md
#   <root>/index.md
#   <root>/manifest.yaml
#   <root>/{compliance,architecture,data,delivery}/
#
# Existing files are preserved unless --force is passed.

set -euo pipefail

PROJECT_ROOT=""
ROOT="references/"
FORCE=false

usage() {
  cat <<'EOF'
Usage: bash scaffold-reference-pack.sh --project-root <repo-root> [--root <path>] [--force]

Options:
  --project-root DIR   Target repository root (required)
  --root PATH          Reference pack root relative to the repo root (default: references/)
  --force              Overwrite README.md, index.md, and manifest.yaml if they already exist
  -h, --help           Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --root) ROOT="$2"; shift 2 ;;
    --force) FORCE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$PROJECT_ROOT" ]]; then
  echo "Missing required arg: --project-root" >&2
  usage
  exit 2
fi

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "Project root does not exist: $PROJECT_ROOT" >&2
  exit 2
fi

ROOT="${ROOT%/}"
TARGET_ROOT="$PROJECT_ROOT/$ROOT"
TODAY="$(date +%F)"

mkdir -p "$TARGET_ROOT"
mkdir -p "$TARGET_ROOT/compliance" "$TARGET_ROOT/architecture" "$TARGET_ROOT/data" "$TARGET_ROOT/delivery"

write_if_needed() {
  local path="$1"
  if [[ -f "$path" && "$FORCE" != true ]]; then
    return 0
  fi
  cat > "$path"
}

write_if_needed "$TARGET_ROOT/README.md" <<EOF
# Reference Pack

This folder holds project-local reference notes used by the Panel Framework.

- Root: \`$ROOT/\`
- Last scaffolded: $TODAY
- Default capture model: metadata_only | summary | local_copy

Start with \`manifest.yaml\` for inventory and \`index.md\` for the human-readable map.
EOF

write_if_needed "$TARGET_ROOT/index.md" <<'EOF'
# Reference Pack Index

| ID | Title | Type | Status | Roles | Path |
|----|-------|------|--------|-------|------|

## Gaps / Watchlist

- Add high-value sources here as the project evolves.
EOF

write_if_needed "$TARGET_ROOT/manifest.yaml" <<EOF
version: 1
root: $ROOT/
generated_by: panel-init
default_capture: summary
last_updated: $TODAY
entries: []
EOF

echo "$TARGET_ROOT"
