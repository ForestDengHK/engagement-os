#!/usr/bin/env bash
# framework-scripts/resolve-output-path.sh — deterministic output-path resolver
#
# Usage:
#   resolve-output-path.sh --project-root <path> --skill <skill> [args]
#
# Required arguments:
#   --project-root <path>   The project root (parent of .claude/)
#   --skill <skill>         One of: discuss | draft | review | debrief | refresh | roles-map
#
# Skill-specific arguments:
#   --thread-id <id>        Required for discuss | draft | review | debrief
#   --date <YYYY-MM-DD>     Required for refresh
#   (roles-map takes no extra args)
#
# Optional:
#   --output <path>         CLI override (highest precedence). Ends in .md → literal; else directory.
#   --print-source          Print the precedence-level source tag instead of the path (for obs footer).
#
# Precedence (highest wins):
#   1. --output=<path>                          source: cli
#   2. config.output_paths.<skill>              source: config.output_paths.<skill>
#   3. config.output_base/<canonical-subdir>/   source: config.output_base
#   4. panel/<canonical-subdir>/                source: fallback
#
# Exits 0 with the resolved absolute path on stdout (or the source tag with --print-source).
# Exits 2 on usage error.

set -eu

PROJECT_ROOT=""
SKILL=""
THREAD_ID=""
DATE=""
CLI_OUTPUT=""
PRINT_SOURCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --skill)        SKILL="$2"; shift 2 ;;
    --thread-id)    THREAD_ID="$2"; shift 2 ;;
    --date)         DATE="$2"; shift 2 ;;
    --output)       CLI_OUTPUT="$2"; shift 2 ;;
    --print-source) PRINT_SOURCE=true; shift ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$PROJECT_ROOT" ]] && { echo "Missing --project-root" >&2; exit 2; }
[[ -z "$SKILL" ]] && { echo "Missing --skill" >&2; exit 2; }

# Canonical per-skill subdir + filename
case "$SKILL" in
  discuss)   SUBDIR="discussions"; [[ -z "$THREAD_ID" ]] && { echo "discuss needs --thread-id" >&2; exit 2; }; FILENAME="$THREAD_ID.md"; CONFIG_KEY="discussions" ;;
  draft)     SUBDIR="drafts";      [[ -z "$THREAD_ID" ]] && { echo "draft needs --thread-id" >&2; exit 2; };   FILENAME="$THREAD_ID.md"; CONFIG_KEY="drafts" ;;
  review)    SUBDIR="reviews";     [[ -z "$THREAD_ID" ]] && { echo "review needs --thread-id" >&2; exit 2; };  FILENAME="$THREAD_ID.md"; CONFIG_KEY="reviews" ;;
  debrief)   SUBDIR="debriefs";    [[ -z "$THREAD_ID" ]] && { echo "debrief needs --thread-id" >&2; exit 2; }; FILENAME="$THREAD_ID.md"; CONFIG_KEY="debriefs" ;;
  refresh)   SUBDIR="refresh";     [[ -z "$DATE" ]] && { echo "refresh needs --date" >&2; exit 2; };           FILENAME="refresh-$DATE.md"; CONFIG_KEY="refresh" ;;
  roles-map) SUBDIR="";            FILENAME="stakeholder-map.md"; CONFIG_KEY="stakeholder_map" ;;
  *) echo "Unknown --skill: $SKILL" >&2; exit 2 ;;
esac

# Read config (flat/nested YAML via awk — no yq dep)
CONFIG="$PROJECT_ROOT/.claude/panel-config.yaml"
OUTPUT_BASE="panel/"
PER_SKILL=""
if [[ -f "$CONFIG" ]]; then
  # output_base (top-level, string)
  val=$(awk '/^output_base:/ { sub(/^output_base:[[:space:]]*/, ""); sub(/[[:space:]]+$/, ""); gsub(/^"|"$/, ""); print; exit }' "$CONFIG")
  [[ -n "$val" && "$val" != "null" ]] && OUTPUT_BASE="$val"
  # output_paths.<CONFIG_KEY> (nested one level, under output_paths:)
  val=$(awk -v key="$CONFIG_KEY" '
    /^output_paths:/ { in_sec=1; next }
    /^[A-Za-z_]/ && in_sec { in_sec=0 }
    in_sec && $0 ~ "^[[:space:]]+" key ":" {
      sub("^[[:space:]]+" key ":[[:space:]]*", "");
      sub(/[[:space:]]+$/, ""); gsub(/^"|"$/, ""); print; exit
    }
  ' "$CONFIG")
  [[ -n "$val" && "$val" != "null" ]] && PER_SKILL="$val"
fi

# Ensure OUTPUT_BASE ends with a slash for consistent joining
[[ "$OUTPUT_BASE" != */ ]] && OUTPUT_BASE="$OUTPUT_BASE/"

# Helper: resolve a relative-or-absolute path against PROJECT_ROOT
abspath() {
  local p="$1"
  if [[ "$p" == /* ]]; then printf '%s' "$p"
  else printf '%s/%s' "$PROJECT_ROOT" "$p"
  fi
}

# Helper: given a path value (might be dir or .md file) + filename, emit the final path
join_with_filename() {
  local p="$1" fn="$2"
  if [[ "$p" == *.md ]]; then
    printf '%s' "$(abspath "$p")"
  else
    [[ "$p" != */ ]] && p="$p/"
    printf '%s%s' "$(abspath "$p")" "$fn"
  fi
}

# Precedence chain
SOURCE=""
FINAL=""
if [[ -n "$CLI_OUTPUT" ]]; then
  FINAL=$(join_with_filename "$CLI_OUTPUT" "$FILENAME")
  SOURCE="cli"
elif [[ -n "$PER_SKILL" ]]; then
  FINAL=$(join_with_filename "$PER_SKILL" "$FILENAME")
  SOURCE="config.output_paths.$CONFIG_KEY=$PER_SKILL"
elif [[ -f "$CONFIG" ]]; then
  if [[ -n "$SUBDIR" ]]; then
    FINAL=$(join_with_filename "${OUTPUT_BASE}${SUBDIR}/" "$FILENAME")
  else
    FINAL=$(join_with_filename "${OUTPUT_BASE}" "$FILENAME")
  fi
  if [[ -n "$SUBDIR" ]]; then
    SOURCE="config.output_base=${OUTPUT_BASE}${SUBDIR}/"
  else
    SOURCE="config.output_base=${OUTPUT_BASE}"
  fi
else
  # Fallback — no config
  if [[ -n "$SUBDIR" ]]; then
    FINAL=$(join_with_filename "panel/${SUBDIR}/" "$FILENAME")
    SOURCE="fallback=panel/${SUBDIR}/"
  else
    FINAL=$(join_with_filename "panel/" "$FILENAME")
    SOURCE="fallback=panel/"
  fi
fi

if $PRINT_SOURCE; then
  printf '%s\n' "$SOURCE"
else
  printf '%s\n' "$FINAL"
fi
