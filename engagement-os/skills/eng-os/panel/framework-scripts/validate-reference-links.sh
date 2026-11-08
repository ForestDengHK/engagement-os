#!/usr/bin/env bash
# validate-reference-links.sh — deterministic bidirectional linkage validator
# for the Panel Framework reference pack.
#
# Usage:
#   validate-reference-links.sh --project-root <dir> [--reference-root <path>]
#
# What it checks
#   1. For every role file under .claude/roles/**/*.md that declares
#      `reference_pack_ids:` in frontmatter:
#        a) each id appears in <reference_root>/manifest.yaml
#        b) the id has exactly one note file on disk whose `id:`
#           frontmatter matches
#        c) that note's `roles:` frontmatter lists the role slug
#           (reverse linkage)
#   2. For every note file under <reference_root>/**/*.md that declares
#      `id:` + `roles:` in frontmatter:
#        a) the id appears in manifest.yaml
#        b) every role slug listed in `roles:` points back via the role's
#           `reference_pack_ids:` (reverse linkage held by the role)
#        c) role slug resolves to a real role file under .claude/roles/**
#
# Exit codes:
#   0 — all checks pass
#   1 — one or more VIOLATIONs reported (printed one per line)
#   2 — usage error / project structure missing
#
# No non-core tools required (awk, grep, sed, find only).
# Called from:
#   - panel-init self-check (optional deterministic pass)
#   - panel-new-role self-check (optional)
#   - panel-refresh Step 5 after reference-pack writes
#   - tests/test-reference-linkage.sh

set -eu

PROJECT_ROOT=""
REFERENCE_ROOT=""

usage() {
  cat <<'EOF'
Usage: bash validate-reference-links.sh --project-root <dir> [--reference-root <path>]

Options:
  --project-root DIR     Project root (must contain .claude/roles/) (required)
  --reference-root PATH  Reference-pack root relative to project root.
                         If omitted, reads `reference_pack_root:` from
                         .claude/panel-config.yaml, else defaults to `references/`.
  -h, --help             Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)   PROJECT_ROOT="$2"; shift 2 ;;
    --reference-root) REFERENCE_ROOT="$2"; shift 2 ;;
    -h|--help)        usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$PROJECT_ROOT" ]]; then
  echo "Missing required arg: --project-root" >&2
  usage
  exit 2
fi
if [[ ! -d "$PROJECT_ROOT/.claude/roles" ]]; then
  echo "Project root missing .claude/roles/: $PROJECT_ROOT" >&2
  exit 2
fi

# Resolve reference_root if not given
if [[ -z "$REFERENCE_ROOT" ]]; then
  if [[ -f "$PROJECT_ROOT/.claude/panel-config.yaml" ]]; then
    val=$(awk '
      /^reference_pack_root:/ {
        sub(/^reference_pack_root:[[:space:]]*/, "")
        # Strip trailing comment (YAML `# ...`) before anything else.
        sub(/[[:space:]]+#.*$/, "")
        sub(/[[:space:]]+$/, "")
        gsub(/^"|"$/, "")
        print
        exit
      }
    ' "$PROJECT_ROOT/.claude/panel-config.yaml")
    [[ -n "$val" ]] && REFERENCE_ROOT="$val"
  fi
  [[ -z "$REFERENCE_ROOT" ]] && REFERENCE_ROOT="references/"
fi
REFERENCE_ROOT="${REFERENCE_ROOT%/}"
REF_DIR="$PROJECT_ROOT/$REFERENCE_ROOT"

VIOLATIONS=0
report() {
  echo "VIOLATION: $1"
  VIOLATIONS=$((VIOLATIONS + 1))
}

# ---------- Frontmatter helpers ----------

# Extract the YAML frontmatter block (lines between the first two '---').
# Prints nothing if the file lacks a frontmatter block.
frontmatter_of() {
  awk '
    NR == 1 && $0 != "---" { exit }
    /^---$/ { n++; if (n == 2) exit; next }
    n == 1 { print }
  ' "$1"
}

# Pull a scalar top-level value (e.g. `id: foo`).
# Strips trailing YAML comments. Does not handle multiline, quoted dicts,
# or nested keys.
fm_scalar() {
  local fm="$1"
  local key="$2"
  echo "$fm" | awk -v k="^${key}:" '
    $0 ~ k {
      sub(/^[^:]+:[[:space:]]*/, "")
      sub(/[[:space:]]+#.*$/, "")
      gsub(/[[:space:]]+$/, "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  '
}

# Pull a list under a top-level key. Accepts either inline `- item` lines
# or an indented block form under `key:`. Returns one value per line.
fm_list() {
  local fm="$1"
  local key="$2"
  echo "$fm" | awk -v k="^${key}:" '
    BEGIN { in_list = 0 }
    $0 ~ k { in_list = 1; next }
    in_list {
      # Stop when we hit another top-level key (non-indented, non-blank, non-bullet).
      if ($0 ~ /^[A-Za-z_][A-Za-z0-9_]*:/) { in_list = 0; next }
      if ($0 ~ /^[[:space:]]*-[[:space:]]+/) {
        val = $0
        sub(/^[[:space:]]*-[[:space:]]+/, "", val)
        gsub(/[[:space:]]+$/, "", val)
        gsub(/^"|"$/, "", val)
        if (val != "") print val
      }
    }
  '
}

# ---------- Load manifest ids ----------

MANIFEST="$REF_DIR/manifest.yaml"
MANIFEST_IDS=""     # newline-separated list of ids declared in manifest
if [[ -f "$MANIFEST" ]]; then
  # A manifest entry id looks like `  - id: <slug>` under `entries:`.
  MANIFEST_IDS=$(awk '
    /^entries:[[:space:]]*$/ { in_entries = 1; next }
    in_entries && /^[A-Za-z_]/ { in_entries = 0 }
    in_entries && /^[[:space:]]*-[[:space:]]*id:[[:space:]]*/ {
      sub(/^[[:space:]]*-[[:space:]]*id:[[:space:]]*/, "")
      gsub(/[[:space:]]+$/, "")
      gsub(/^"|"$/, "")
      print
    }
  ' "$MANIFEST")
elif [[ -d "$REF_DIR" ]]; then
  report "manifest.yaml missing at $MANIFEST (reference pack exists but has no inventory)."
fi

manifest_has_id() {
  local target="$1"
  [[ -z "$MANIFEST_IDS" ]] && return 1
  while IFS= read -r id; do
    [[ "$id" == "$target" ]] && return 0
  done <<< "$MANIFEST_IDS"
  return 1
}

# ---------- Index note files by id ----------

# Build two arrays: NOTE_ID[i] and NOTE_PATH[i] for every note file under REF_DIR.
declare -a NOTE_IDS=()
declare -a NOTE_PATHS=()
declare -a NOTE_ROLES=()   # parallel: each index is the raw newline-joined role slug list

if [[ -d "$REF_DIR" ]]; then
  while IFS= read -r note_file; do
    # Skip the top-level README / index / template-ish files.
    [[ "$(basename "$note_file")" == "README.md" ]] && continue
    [[ "$(basename "$note_file")" == "index.md" ]] && continue

    fm=$(frontmatter_of "$note_file")
    [[ -z "$fm" ]] && continue

    nid=$(fm_scalar "$fm" "id")
    [[ -z "$nid" ]] && continue

    roles_list=$(fm_list "$fm" "roles")

    NOTE_IDS+=("$nid")
    NOTE_PATHS+=("$note_file")
    NOTE_ROLES+=("$roles_list")
  done < <(find "$REF_DIR" -type f -name '*.md' 2>/dev/null)
fi

note_index_of_id() {
  local target="$1"
  local i=0
  local n=${#NOTE_IDS[@]}
  [[ "$n" -eq 0 ]] && return 1
  while [[ "$i" -lt "$n" ]]; do
    if [[ "${NOTE_IDS[$i]}" == "$target" ]]; then
      echo "$i"
      return 0
    fi
    i=$((i + 1))
  done
  return 1
}

# ---------- Index role files ----------

declare -a ROLE_NAMES=()
declare -a ROLE_PATHS=()
declare -a ROLE_REFIDS=()   # parallel: newline-joined reference_pack_ids list

while IFS= read -r role_file; do
  [[ "$(basename "$role_file")" == "_README.md" ]] && continue
  fm=$(frontmatter_of "$role_file")
  [[ -z "$fm" ]] && continue

  rname=$(fm_scalar "$fm" "name")
  [[ -z "$rname" ]] && continue

  refids=$(fm_list "$fm" "reference_pack_ids")

  ROLE_NAMES+=("$rname")
  ROLE_PATHS+=("$role_file")
  ROLE_REFIDS+=("$refids")
done < <(find "$PROJECT_ROOT/.claude/roles" -type f -name '*.md' 2>/dev/null)

role_exists() {
  local target="$1"
  local i=0
  local n=${#ROLE_NAMES[@]}
  while [[ "$i" -lt "$n" ]]; do
    [[ "${ROLE_NAMES[$i]}" == "$target" ]] && return 0
    i=$((i + 1))
  done
  return 1
}

role_has_refid() {
  local role="$1"
  local want="$2"
  local i=0
  local n=${#ROLE_NAMES[@]}
  while [[ "$i" -lt "$n" ]]; do
    if [[ "${ROLE_NAMES[$i]}" == "$role" ]]; then
      while IFS= read -r id; do
        [[ "$id" == "$want" ]] && return 0
      done <<< "${ROLE_REFIDS[$i]}"
      return 1
    fi
    i=$((i + 1))
  done
  return 1
}

# ---------- Forward-direction checks: role -> note ----------

i=0
n_roles=${#ROLE_NAMES[@]}
while [[ "$i" -lt "$n_roles" ]]; do
  rname="${ROLE_NAMES[$i]}"
  refids="${ROLE_REFIDS[$i]}"
  rpath="${ROLE_PATHS[$i]}"
  i=$((i + 1))
  [[ -z "$refids" ]] && continue

  while IFS= read -r refid; do
    [[ -z "$refid" ]] && continue

    # (1a) id must appear in manifest.yaml
    if ! manifest_has_id "$refid"; then
      report "role '$rname' ($rpath) declares reference_pack_id '$refid', but it is not listed in $REFERENCE_ROOT/manifest.yaml entries."
    fi

    # (1b) id must resolve to a note file
    if ! nidx=$(note_index_of_id "$refid"); then
      report "role '$rname' declares reference_pack_id '$refid', but no note file under $REFERENCE_ROOT/ has frontmatter 'id: $refid'."
      continue
    fi

    # (1c) that note's roles: list must contain this role slug
    note_path="${NOTE_PATHS[$nidx]}"
    note_roles="${NOTE_ROLES[$nidx]}"
    found_reverse=false
    while IFS= read -r nr; do
      [[ "$nr" == "$rname" ]] && { found_reverse=true; break; }
    done <<< "$note_roles"
    if ! $found_reverse; then
      report "role '$rname' links to reference '$refid' ($note_path), but that note's 'roles:' frontmatter does not list '$rname' — reverse linkage missing."
    fi
  done <<< "$refids"
done

# ---------- Reverse-direction checks: note -> role ----------

i=0
n_notes=${#NOTE_IDS[@]}
while [[ "$i" -lt "$n_notes" ]]; do
  nid="${NOTE_IDS[$i]}"
  note_path="${NOTE_PATHS[$i]}"
  nroles="${NOTE_ROLES[$i]}"
  i=$((i + 1))

  # (2a) id must appear in manifest.yaml
  if ! manifest_has_id "$nid"; then
    report "note '$nid' ($note_path) is on disk but not listed in $REFERENCE_ROOT/manifest.yaml entries."
  fi

  # (2b)+(2c): each listed role must exist and point back
  while IFS= read -r rslug; do
    [[ -z "$rslug" ]] && continue
    if ! role_exists "$rslug"; then
      report "note '$nid' ($note_path) lists role '$rslug' in its roles:, but no role file with name '$rslug' exists under .claude/roles/."
      continue
    fi
    if ! role_has_refid "$rslug" "$nid"; then
      report "note '$nid' lists role '$rslug', but that role's reference_pack_ids: does not include '$nid' — reverse linkage missing."
    fi
  done <<< "$nroles"
done

# ---------- Result ----------

echo "Total violations: $VIOLATIONS"
if [[ "$VIOLATIONS" -gt 0 ]]; then
  exit 1
fi
exit 0
