#!/usr/bin/env python3
"""vendored_skills.py — skills this repo ships as copies of another repo's skills.

`designing-figures` and `presentation-builder` are written and loaded from forest-skills
(`~/.claude/skills/<name>` symlinks into it). forest-skills is a private repo, so a plugin in
this public marketplace cannot point at it — deck-craft ships a vendored copy instead. A copy
nobody refreshes goes stale silently (deck-craft still said "default output is a PNG" after
forest-skills had moved decks to native PowerPoint), so this script diffs each copy against
its source and, with --sync, overwrites the copy.

The panel skills and framework-scripts bundled in engagement-os (`skills/eng-os/panel/`, planted
into engagement repos by the scaffolder) are copies of panel-framework, synced the same way.

    python3 scripts/vendored_skills.py            # check: list drift
    python3 scripts/vendored_skills.py --sync     # make every copy identical to its source

Edit the skill in its source repo, never here; then --sync and commit both repos.
Source roots: $FOREST_SKILLS (default ~/working/forest-skills/skills),
$PANEL_FRAMEWORK (default ~/working/panel-framework).

Private skills carry client cases, so every source is first scanned by forest-skills'
public_guard.py ($PUBLIC_GUARD_SCRIPT, default ~/working/forest-skills/scripts/public_guard.py;
its name list stays in forest-skills and never comes here). A source with a hit is reported as
LEAK and --sync refuses to copy it. No guard → skipped with a message.
Exit 0 no drift (a missing source root is skipped, not passed) · 1 drift or leak found.
"""
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = {
    "forest-skills": Path(os.environ.get("FOREST_SKILLS") or Path.home() / "working" / "forest-skills" / "skills"),
    "panel-framework": Path(os.environ.get("PANEL_FRAMEWORK") or Path.home() / "working" / "panel-framework"),
}
PANEL = "engagement-os/skills/eng-os/panel"
VENDORED = [                                    # (copy in this repo, source repo, path in the source repo)
    ("deck-craft/skills/designing-figures", "forest-skills", "designing-figures"),
    ("deck-craft/skills/presentation-builder", "forest-skills", "presentation-builder"),
    (f"{PANEL}/framework-scripts", "panel-framework", "framework-scripts"),
] + [(f"{PANEL}/skills/{n}", "panel-framework", f"skills/{n}") for n in
     ("panel-discuss", "panel-edit-role", "panel-init", "panel-new-role", "panel-refresh", "panel-review", "panel-roles")]
IGNORE = ["__pycache__", "*.pyc", ".DS_Store"]
GUARD = Path(os.environ.get("PUBLIC_GUARD_SCRIPT")
             or Path.home() / "working" / "forest-skills" / "scripts" / "public_guard.py")


def leaks(roots):
    """{(source root, name): ["file:line: term", ...]} for sources holding a name; None when the guard is absent."""
    if not GUARD.is_file():
        return None
    out = {}
    for root in roots:
        names = [n for _, r, n in VENDORED if r == root]
        r = subprocess.run([sys.executable, str(GUARD), "scan", "--repo", str(SOURCES[root]), "--files", *names],
                           capture_output=True, text=True)
        if r.returncode > 1:
            sys.exit(f"public guard failed: {r.stderr.strip()}")
        for ln in r.stdout.splitlines():
            name = next((n for n in names if ln.startswith(f"{n}/")), None)
            if name:
                out.setdefault((root, name), []).append(ln[len(name) + 1:])
            else:
                print(ln)                                       # "public guard: no list, nothing checked"
    return out


def drift(a, b, rel=""):
    """Paths under rel that differ between dirs a and b, or exist in only one."""
    if not b.is_dir():
        return [f"{rel or './'} (copy missing)"]
    c = filecmp.dircmp(a, b, ignore=IGNORE)
    out = [f"{rel}{n} (only in source)" for n in c.left_only] + [f"{rel}{n} (only in copy)" for n in c.right_only]
    out += [f"{rel}{n}" for n in c.common_funny + c.funny_files]
    out += [f"{rel}{n}" for n in c.common_files               # dircmp alone compares shallowly
            if not filecmp.cmp(a / n, b / n, shallow=False)]
    for d in c.common_dirs:
        out += drift(a / d, b / d, f"{rel}{d}/")
    return sorted(out)


def main():
    sync = "--sync" in sys.argv[1:]
    found = leaked = 0
    for root in sorted({r for _, r, _ in VENDORED if not SOURCES[r].is_dir()}):
        print(f"SKIPPED: {root} not found at {SOURCES[root]} — its copies were not checked")
    bad = leaks(sorted({r for _, r, _ in VENDORED if SOURCES[r].is_dir()}))
    if bad is None:
        print(f"SKIPPED: public guard not found at {GUARD} — sources were not checked for names")
    for copy, root, name in VENDORED:
        if not SOURCES[root].is_dir():
            continue
        src, dst = SOURCES[root] / name, REPO / copy
        diffs = drift(src, dst)
        hits = (bad or {}).get((root, name))
        if hits:
            leaked += 1
            print(f"LEAK    {src} has names a public repo must not carry"
                  + (" — not synced" if sync else "") + ":\n" + "\n".join(f"          {h}" for h in hits))
        if diffs and sync and hits:
            continue
        if diffs and sync:
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORE))
            print(f"synced  {copy} <- {src} ({len(diffs)} paths)")
        elif diffs:
            found += 1
            print(f"DRIFT   {copy} vs {src}:\n" + "\n".join(f"          {d}" for d in diffs))
        elif not hits:
            print(f"same    {copy}")
    if found:
        print(f"\n{found} vendored skill(s) differ from their source — run with --sync, then commit.")
    if leaked:
        print(f"\n{leaked} source skill(s) carry client, colleague or personal names — remove them in the source repo "
              "(or allowlist a false hit in forest-skills/config/public-guard.txt), then --sync.")
    return 1 if found or leaked else 0


if __name__ == "__main__":
    sys.exit(main())
